import re
import html
from environment import logging
import datetime
from db_repo.oauth_tokens_repo import Oauth_tokens as Oauth_tokens_repo
from db_repo.user_repo import User as User_repo
from db_repo.totp_secret_repo import TOTP_secret as TOTP_secret_repo
from db_repo.zke_repo import ZKE as ZKE_encryption_key_repo
from db_repo.google_drive_integration_repo import GoogleDriveIntegration as GoogleDriveIntegration_repo
from db_repo.preferences_repo import Preferences as Preferences_repo
from db_repo.email_verification_repo import EmailVerificationToken
import os
from hashlib import sha256
from base64 import b64encode
import requests
from Email import send as send_email
import ipaddress
from jsonschema import validate, ValidationError



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
        logging.info("name =" +file.get("name"))
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
    ZKE_encryption_key_repo().delete(user_id)
    User_repo().delete(user_id)
    logging.info("User " + str(user_id) + " deleted from database")


def generate_new_email_verification_token(user_id):
    email_verification_token_repo = EmailVerificationToken()
    email_verification_token_repo.delete(user_id)
    token = b64encode(os.urandom(5)).decode()
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

# Return format : ip (city region name zip country)
# If the IP address is private it is set to unknow to not leak information
def get_geolocation(ip):
    try:
        logging.info("Getting geolocation for ip " + str(ip))  
        r = requests.get("http://ip-api.com/json/" + str(ip) )# nosemgrep
        if r.status_code != 200:
            return "unknown (unknown, unknown)"
        json = r.json()
        if json["status"] != "success":
            return "unknown (unknown, unknown)"
        return f"{ip} ({json['zip']} {json['city']}, {json['regionName']}, {json['country']})"
    except Exception as e:
        logging.error("Error while getting geolocation : " + str(e))
        return "unknown (unknown, unknown)"

def get_ip(request):
    def test_ip(ip):
        try:
            if(ipaddress.ip_address(ip).is_private):
                return False
            return True
        except Exception as e:
            return False
        
    remote_ip = request.remote_addr
    forwarded_for = request.headers.get("X-Forwarded-For", request.remote_addr)
    if test_ip(remote_ip):
        return remote_ip
    elif test_ip(forwarded_for):
        return forwarded_for
    else:
        logging.error("Could not get ip address from request. Remote ip : " + str(remote_ip) + " Forwarded for : " + str(forwarded_for))
        return None

def unsafe_json_vault_validation(json:str) -> (bool, str):
    print("len = ", len(json))
    if len(json) > 4 * 1024 *1024:
        return False, "The vault is too big. The maximum size is 4MB"
    schema = {
        "type": "object",
        "properties": {
            "uuid": {"type": "string"},
        },
        "required": ["uuid"]
    }
    try:
        validate(json, schema)
        return True, "OK"
    except Exception as e:
        return False, "The vault submitted is invalid. If you submitted this vault through the web interface, please report this issue to the support."
    