from app import app
import re
import html
from environment import logging
import datetime
from database.oauth_tokens_repo import Oauth_tokens as Oauth_tokens_repo
from database.user_repo import User as User_repo
from database.totp_secret_repo import TOTP_secret as TOTP_secret_repo
from database.zke_repo import ZKE as ZKE_encryption_key_repo
from database.google_drive_integration_repo import GoogleDriveIntegration as GoogleDriveIntegration_repo
from database.preferences_repo import Preferences as Preferences_repo
from database.email_verification_repo import EmailVerificationToken
from database.rate_limiting_repo import RateLimitingRepo 
from database.refresh_token_repo import RefreshTokenRepo
from database.session_token_repo import SessionTokenRepo
from database.backup_configuration_repo import BackupConfigurationRepo
import os
from hashlib import sha256
from base64 import b64encode
import requests
from Email import send as send_email
import ipaddress
from jsonschema import validate, ValidationError
from environment import conf
import geoip2.database


class FileNotFound(Exception):
    pass

class CorruptedFile(Exception):
     pass

def check_email(email):
    email_regex = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    if len(email) > 250:
        return False
    return re.match(email_regex, email) and re.search(email_regex, email).group() == email


def sanitize_input(string) -> str:
    string = string.replace("'", "")
    string = string.replace('"', "")
    return html.escape(string)

def get_all_secrets_sorted(totp_secrets_list):
    secrets = []
    for secret in totp_secrets_list:
        secrets.append({"uuid": secret.uuid, "enc_secret": secret.secret_enc})
    return sorted(secrets,key=lambda x: x["uuid"])

def extract_last_backup_from_list(files_list) -> (any, datetime):
    last_backup_file_date = None
    last_backup_file = None
    for file in files_list:
        logging.debug("name =" +file.get("name"))
        if "_backup" not in file.get("name") or file.get('explicitlyTrashed'):
            continue
        date_str = file.get("name").split("_")[0]
        try:
          date = datetime.datetime.strptime(date_str, '%d-%m-%Y-%H-%M-%S')
        except Exception as e:
              logging.info("Error while parsing date : " + str(e) + " (file name : " + file.get("name") + ". Ignoring this file")
              continue
        if last_backup_file_date is None:
            last_backup_file_date = date
            last_backup_file = file
        elif date > last_backup_file_date:
              last_backup_file_date = date
              last_backup_file = file
    if last_backup_file is None:
        logging.info("No backup file found in the drive (last_backup_file is None)")
        raise FileNotFound("No backup file found")
    return last_backup_file,last_backup_file_date

 
def delete_user_from_database(user_id):
    Oauth_tokens_repo().delete(user_id)
    GoogleDriveIntegration_repo().delete(user_id)
    Preferences_repo().delete(user_id)
    TOTP_secret_repo().delete_all(user_id)
    BackupConfigurationRepo().delete(user_id)
    ZKE_encryption_key_repo().delete(user_id)
    EmailVerificationToken().delete(user_id)
    RateLimitingRepo().flush_by_user_id(user_id)
    SessionTokenRepo().delete_by_user_id(user_id)
    RefreshTokenRepo().delete_by_user_id(user_id)
    User_repo().delete(user_id)
    logging.info("User " + str(user_id) + " deleted from database")


def generate_new_email_verification_token(user_id):
    email_verification_token_repo = EmailVerificationToken()
    email_verification_token_repo.delete(user_id)
    token = os.urandom(5).hex()
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    email_verification_token_repo.add(user_id, token,expiration.timestamp())
    return token

def send_information_email(ip, email, reason):
    logging.info(str(reason)+ str(ip) + str(email))
    date = str(datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")) + " UTC"
    
    ip_and_geo = get_geolocation(ip)
    try:
        send_email.send_information_email(email, reason=reason, date=date, ip=ip_and_geo)
    except Exception as e:
        logging.error("Unknown error while sending information email" + str(e))

# Return format : ip (city region country)
# If the geolocation is disabled  the function will return only the IP address
# If the IP is private, the function will return an empty string to avoid leaking private IPs
def get_geolocation(ip):
    if ipaddress.ip_address(ip).is_private:
        return ""
    if conf.features.ip_geolocation.enabled == False:
        return str(ip) 
    logging.info("Getting geolocation for ip " + str(ip))  
    result = str(ip)
    try:
        with geoip2.database.Reader(conf.features.ip_geolocation.geoip_database_path) as reader:
            geo = reader.city(ip)
            city = geo.city.name + ", " if geo.city.name != None else ""
            region = geo.subdivisions.most_specific.name + ", " if geo.subdivisions.most_specific.name != None else ""
            country = ""
            if geo.country.name != None: 
                country = geo.country.name 
            elif geo.registered_country.name != None:
                country = geo.registered_country.name 
            result = f"{ip} ({city}{region}{country})"
    except Exception as e:
        logging.error("Error while getting geolocation for ip " + str(ip) + " : " + str(e))
    return result

def get_ip(request):
    def test_ip(ip):
        try:
            if(ip.is_private):
                return False
            return True
        except Exception as e:
            logging.error("Error while testing ip address : " + str(e))
            return False
    try:
        with app.app.app_context():
            remote_ip = ipaddress.ip_address(request.remote_addr)
    except Exception as e:
        logging.error("Error while getting remote ip address : " + str(e))
        return None
    is_remote_ip_a_trusted_proxy = False
    if conf.api.trusted_proxy != None:
        for ip_network in conf.api.trusted_proxy:
            if remote_ip in ip_network:
                is_remote_ip_a_trusted_proxy = True
                break

    if is_remote_ip_a_trusted_proxy:
        if "X-Forwarded-For" in request.headers:
            try:
                #Ipv6 in priority
                forwarded_ip = re.search(r'\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:)))(%.+)?\s*', request.headers["X-Forwarded-For"])
                if forwarded_ip != None:
                    forwarded_ip = forwarded_ip.group(0)
                else:
                    # Ipv4
                    forwarded_ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', request.headers["X-Forwarded-For"])[0]
                    if forwarded_ip == []:
                        logging.error("Could not get ip address from request. No IPv6 or IPv4 found in the header. Forwarded ip : " + str(request.headers["X-Forwarded-For"]))
                        return None
                if test_ip(ipaddress.ip_address(forwarded_ip)):
                    return forwarded_ip
                else:
                    logging.error("Could not get ip address from request. The forwarded IP was not a valid ip address. Test didn't pass, IP very likely to be private. Forwarded ip : " + str(forwarded_ip))
                    return None
            except Exception as e:
                logging.error("Could not get ip address from request. Error while parsing forwarded ip : " + str(e) + ". Forwarded ip : " + str(request.headers["X-Forwarded-For"]))
                return None
        else:
            logging.error("Could not get ip address from request. The request was made through a trusted proxy but the X-Forwarded-For header was not set.")
            return None
    else:
        if test_ip(remote_ip):
            return str(remote_ip)
        else:
            logging.error("Could not get ip address from request. The remote IP was NOT a trusted proxy. Remote ip : " + str(remote_ip))
            return None

def unsafe_json_vault_validation(json:str) -> (bool, str):
    if len(json) > 4 * 1024 *1024:
        return False, "The vault is too big. The maximum size is 4MB"
    schema = {
        "type": "object",
        "patternProperties": {
            "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$": {"type": "string"},
        },
            "additionalProperties": False
    }
    try:
        validate(json, schema)
        return True, "OK"
    except Exception as e:
        logging.error("Error while validating vault json : " + str(e))
        print(e)
        return False, "The vault submitted is invalid. If you submitted this vault through the web interface, please report this issue to the support."


def revoke_session(session_id=None, refresh_id=None):
    logging.info(f"Revoking session {session_id} and refresh {refresh_id}")
    session_repo = SessionTokenRepo()
    refresh_repo = RefreshTokenRepo()
    session = session_repo.get_session_token_by_id(session_id)
    refresh = refresh_repo.get_refresh_token_by_id(refresh_id)
    if session != None:
        session_repo.revoke(session.id)
        logging.info(f"Revoked session {session.id}")
        if not refresh or refresh.session_token_id != session.id:
            associated_refresh = refresh_repo.get_refresh_token_by_session_id(session.id)
            logging.info(f"Revoked refresh {session.id} because the associated session {session.id} was revoked")
            refresh_repo.revoke(associated_refresh.id) if associated_refresh != None else None
    if refresh != None:
        refresh_repo.revoke(refresh.id)
        logging.info(f"Revoked refresh {refresh.id}")
        if not session or session.id != refresh.session_token_id:
            associated_session = session_repo.get_session_token_by_id(refresh.session_token_id)
            session_repo.revoke(associated_session.id) if  associated_session != None else None
            logging.info(f"Revoked session {associated_session.id} because the associated refresh {refresh.id} was revoked")
    return True