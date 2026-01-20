from flask import request, redirect, make_response
from Utils.http_response import Response
import flask
import connexion
import json
from database.user_repo import User as UserDB
from database.zke_repo import ZKE as ZKE_DB
from database.totp_secret_repo import TOTP_secret as TOTP_secretDB
from database.google_drive_integration_repo import GoogleDriveIntegration as GoogleDriveIntegrationDB
from database.preferences_repo import Preferences as PreferencesDB
from database.notif_repo import Notifications as Notifications_db
from database.refresh_token_repo import RefreshTokenRepo as RefreshToken_db
from database.rate_limiting_repo import RateLimitingRepo as Rate_Limiting_DB
from database.session_token_repo import SessionTokenRepo 
from database.session_repo import SessionRepo
from CryptoClasses.hash_func import Bcrypt
from environment import logging, conf
from database.oauth_tokens_repo import Oauth_tokens as Oauth_tokens_db
from CryptoClasses.hash_func import Bcrypt
from Oauth import google_drive_api
import random
import string
from Email import send as send_email
from database.email_verification_repo import EmailVerificationToken as EmailVerificationToken_db
from CryptoClasses.sign_func import API_signature
from CryptoClasses import refresh_token as refresh_token_func
import Oauth.oauth_flow as oauth_flow
import Utils.utils as utils
import os
import base64
import datetime
from Utils.security_wrapper import  require_valid_user, require_passphrase_verification,require_valid_user, require_userid, ip_rate_limit
import traceback
from hashlib import sha256
from CryptoClasses.encryption import ServiceSideEncryption 
from database.db import db
import threading
from uuid import uuid4
import hmac
import hashlib
from sqlalchemy import text
from CryptoClasses.serverRSAKeys import ServerRSAKeys
 






if conf.environment.type == "development":
    logging.getLogger().setLevel(logging.INFO)


# POST /signup
def signup():
    if not conf.features.signup_enabled:
        return {"message": "Signup is disabled", "code":"signup_disabled"}, 403
    try:
        data = request.get_json()
        username = utils.sanitize_input(data["username"].strip())
        passphrase = data["password"].strip()
        email = utils.sanitize_input(data["email"].strip())
        derivedKeySalt = utils.sanitize_input(data["derivedKeySalt"].strip())
        zke_key = utils.sanitize_input(data["ZKE_key"].strip())
        passphraseSalt = utils.sanitize_input(data["passphraseSalt"].strip())
    except Exception as e: # pragma: no cover
        logging.info(e)
        return {"message": "Invalid request"}, 400
    
    if not username or not passphrase or not email or not derivedKeySalt or not zke_key or not passphraseSalt:
        return {"message": "Missing parameters"}, 400
    if len(username) > 250:
        return {"message": "Username is too long"}, 400
    if not utils.check_email(email) :
        return {"message": "Bad email format"}, 401
    userDB = UserDB()
    user = userDB.getByEmail(email)
    if user:
        return {"message": "User already exists"}, 409
    check_username = userDB.getByUsername(username)
    if check_username:
        return {"message": "Username already exists"}, 409
    bcrypt = Bcrypt(passphrase)
    try : 
        hashedpw = bcrypt.hashpw()
    except ValueError as e:
        logging.debug(e)
        return {"message": "Password is too long"}, 400
    except Exception as e:
        logging.warning("Uknown error occured while hashing password" + str(e))
        return {"message": "Unknown error while hashing your password"}, 500
    try:
        today = datetime.datetime.now().strftime("%d/%m/%Y")
        user = userDB.create(username=username, email=email, password=hashedpw, randomSalt=derivedKeySalt, isVerified=0,isBlocked=0, passphraseSalt=passphraseSalt, today=today)
    except Exception as e:
        logging.error("Unknown error while creating user" + str(e))
        return {"message": "Unknown error while creating user"}, 500
    if user :
        try:
            zke_db = ZKE_DB()
            zke_key = zke_db.create(user.id, zke_key)
        except Exception as e:
           zke_key = None
        if zke_key:
            ip = utils.get_ip(request)
            session_token, refresh_token = utils.generate_new_session(user=user, ip_address=ip)
            if conf.features.emails.require_email_validation:
                try:
                    send_verification_email(user=user.id, context_={"user":user.id}, token_info={"user":user.id})
                except Exception as e:
                    logging.error("Unknown error while sending verification email" + str(e))
            response = Response(status=201, mimetype="application/json", response=json.dumps({"message": "User created", "email_verification_required":conf.features.emails.require_email_validation}))
            response.set_auth_cookies(session_token, refresh_token)
            return response
        else :
            userDB.delete(user.id)
            logging.error("Unknown error while storing user ZKE keys" + str(username))
            return {"message": "Unknown error while registering user encrypted keys"}, 500
    else :
        logging.error("Unknown error while creating user" + str(username))
        return {"message": "Unknown error while creating user"}, 500



# POST /login
@ip_rate_limit
def login(ip, body):
    passphrase = body["password"].strip()
    email = utils.sanitize_input(body["email"]).strip()
    rate_limiting_db = Rate_Limiting_DB()
    if not passphrase or not email:
        return {"message": "generic_errors.missing_params"}, 400
    if(not utils.check_email(email) ):
        return {"message": "generic_errors.bad_email"}, 403
    userDB = UserDB()
    user = userDB.getByEmail(email)
    bcrypt = Bcrypt(passphrase)
    if not user:
        logging.info("User " + str(email) + " tried to login but does not exist. A fake password is checked to avoid timing attacks")
        fakePassword = ''.join(random.choices(string.ascii_letters, k=random.randint(10, 20)))
        bcrypt.checkpw(fakePassword)
        
        rate_limiting_db.add_failed_login(ip)
        return {"message": "generic_errors.invalid_creds"}, 403
    logging.info(f"User {user.id} is trying to logging in from gateway {request.remote_addr} and IP {ip}. X-Forwarded-For header is {request.headers.get('X-Forwarded-For')}")
    checked = bcrypt.checkpw(user.password)
    if not checked:
        rate_limiting_db.add_failed_login(ip, user.id)
        return {"message": "generic_errors.invalid_creds"}, 403
    if user.isBlocked: # only authenticated users can see the blocked status
        return {"message": "blocked"}, 403
    
    rate_limiting_db.flush_login_limit(ip)

    session_token, refresh_token = utils.generate_new_session(user=user, ip_address=ip)
    if not conf.features.emails.require_email_validation: # we fake the isVerified status if email validation is not required
        response = Response(status=200, mimetype="application/json", response=json.dumps({"username": user.username, "id":user.id, "derivedKeySalt":user.derivedKeySalt, "isGoogleDriveSync": GoogleDriveIntegrationDB().is_google_drive_enabled(user.id), "role":user.role, "isVerified":True}))
    elif user.isVerified:
        response = Response(status=200, mimetype="application/json", response=json.dumps({"username": user.username, "id":user.id, "derivedKeySalt":user.derivedKeySalt, "isGoogleDriveSync": GoogleDriveIntegrationDB().is_google_drive_enabled(user.id), "role":user.role, "isVerified":user.isVerified}))
    else:
        response = Response(status=200, mimetype="application/json", response=json.dumps({"isVerified":user.isVerified}))
    userDB.update_last_login_date(user.id)
    response.set_auth_cookies(session_token, refresh_token)
    return response

#POST logout
@require_valid_user
def logout(_):
    session_token = request.cookies.get("session-token")
    session_repo = SessionTokenRepo()
    session = session_repo.get_session_token(session_token)
    if not session:
        return {"message": "Session not found"}, 404
    utils.revoke_session(session_id=session.session.id)
    response = Response(status=200, mimetype="application/json", response=json.dumps({"message": "Logged out"}))
    response.delete_cookie("session-token")
    response.delete_cookie("refresh-token")
    return response


#GET /login/specs
def get_login_specs(username):
    rate_limiting_db = Rate_Limiting_DB()
    logging.debug("User " + str(username) + " is trying to get login specs")
    ip = utils.get_ip(request)
    if ip:
        if rate_limiting_db.is_login_rate_limited(ip):
            return {"message": "Too many requests", 'ban_time':conf.features.rate_limiting.login_ban_time}, 429
    if(not utils.check_email(username)):
        return {"message": "Bad request"}, 400
    userDB = UserDB()
    user = userDB.getByEmail(username)
    if user :
        return {"passphrase_salt": user.passphraseSalt}, 200
    else :
        fake_salt = base64.b64encode(os.urandom(16)).decode("utf-8")
        return {"passphrase_salt": fake_salt}, 200

    

    
    
#GET /encrypted_secret/{uuid}
@require_valid_user
def get_encrypted_secret(user_id, uuid):
    totp_secretDB =  TOTP_secretDB()
    enc_secret = totp_secretDB.get_enc_secret_of_user_by_uuid(user_id, uuid)
    if not enc_secret:
        return {"message": "Forbidden"}, 403
    else:
        if enc_secret.user_id == user_id:
            return {"enc_secret": enc_secret.secret_enc}, 200
        else :    
            logging.warning("User " + str(user_id) + " tried to access secret " + str(uuid) + " which is not his")
            return {"message": "Forbidden"}, 403
        
#POST /encrypted_secret
@require_valid_user
def add_encrypted_secret(user_id, body):
    enc_secret = utils.sanitize_input(body["enc_secret"]).strip()
    secret_uuid = ""
    totp_secretDB =  TOTP_secretDB()
    while secret_uuid == "":
        tmp_uuid = str(uuid4())
        if not totp_secretDB.get_enc_secret_by_uuid(tmp_uuid):
            secret_uuid = tmp_uuid
        
    if totp_secretDB.add(user_id, enc_secret, secret_uuid):
        return {"uuid": secret_uuid}, 201
    else :
        logging.warning("Unknown error while adding encrypted secret for user " + str(user_id))
        return {"message": "Unknown error while adding encrypted secret"}, 500

#PUT /encrypted_secret/{uuid}
@require_valid_user
def update_encrypted_secret(user_id,uuid, body):
    enc_secret = body["enc_secret"]
    
    totp_secretDB =  TOTP_secretDB()
    totp = totp_secretDB.get_enc_secret_of_user_by_uuid(user_id, uuid)
    if not totp:
        logging.warning("User " + str(user_id) + " tried to update secret " + str(uuid) + " which does not exist")
        return {"message": "Forbidden"}, 403
    else:
        if totp.user_id != user_id:
            logging.warning("User " + str(user_id) + " tried to update secret " + str(uuid) + " which is not his")
            return {"message": "Forbidden"}, 403
        totp = totp_secretDB.update_secret(uuid=uuid, enc_secret=enc_secret, user_id=user_id)
        if totp == None:
                logging.warning("User " + str(user_id) + " tried to update secret " + str(uuid) + " but an error occurred server side while storing your encrypted secret")
                return {"message": "An error occurred server side while storing your encrypted secret"}, 500
        else:
                return {"message": "Encrypted secret updated"}, 201

#DELETE /encrypted_secret/{uuid}
@require_valid_user
def delete_encrypted_secret(user_id,uuid):
    if(uuid == ""):
        return {"message": "Invalid request"}, 400
    totp_secretDB =  TOTP_secretDB()
    totp = totp_secretDB.get_enc_secret_of_user_by_uuid(user_id, uuid)
    if not totp:
        logging.debug("User " + str(user_id) + " tried to delete secret " + str(uuid) + " which does not exist")
        return {"message": "Forbidden"}, 403
    else:
        if totp.user_id != user_id:
            logging.warning("User " + str(user_id) + " tried to delete secret " + str(uuid) + " which is not his")
            return {"message": "Forbidden"}, 403
        if totp_secretDB.delete(uuid=uuid, user_id= user_id):
            return {"message": "Encrypted secret deleted"}, 201
        else:
            logging.warning("Unknown error while deleting encrypted secret for user " + str(user_id) )
            return {"message": "Unknown error while deleting encrypted secret"}, 500
        

#GET /all_secrets
@require_valid_user
def get_all_secrets(user_id):
    totp_secretDB =  TOTP_secretDB()
    enc_secrets = totp_secretDB.get_all_enc_secret_by_user_id(user_id)
    if not enc_secrets:
        return {"message": "No secret found"}, 404
    else:
        secrets = []
        for enc_secret in enc_secrets:
           secret = {"uuid": enc_secret.uuid, "enc_secret": enc_secret.secret_enc}
           secrets.append(secret)
        return {"enc_secrets": secrets}, 200


#GET /zke_encrypted_key
@require_valid_user
def get_ZKE_encrypted_key(user_id):
        logging.info(user_id)
        zke_db = ZKE_DB()
        zke_key = zke_db.getByUserId(user_id)
        if zke_key:
                return {"zke_encrypted_key": zke_key.ZKE_key}, 200
        else:
            return {"message": "No ZKE key found for this user"}, 404



#PUT /update/email
@require_userid
def update_email(user_id,body):
   
    email = utils.sanitize_input(body["email"]).strip()
    if not utils.check_email(email):
        return {"message": "This email doesn't have the right format. Check it and try again"}, 400
         
    userDb = UserDB()
    already_existing_user = userDb.getByEmail(email)
    if already_existing_user:
        if already_existing_user.id == user_id:
            return {"message":email},201
        else:
            return {"message": "This email already exists"}, 403
    old_mail = userDb.getById(user_id).mail
    user = userDb.update_email(user_id=user_id, email=email, isVerified=0)
    if user:
        try:
            ip = utils.get_ip(request)
            thread = threading.Thread(target=utils.send_information_email,args=(ip, old_mail, "Your email address has been updated"))
            thread.start()
        except Exception as e:
            logging.error("Unknown error while sending information email" + str(e))
        if conf.features.emails.require_email_validation:
            try:
           
                send_verification_email(user=user_id, context_={"user":user_id}, token_info={"user":user_id})
            except Exception as e:
                logging.error("Unknown error while sending verification email" + str(e))
            return {"message":user.mail},201
        else:
            return {"message":user.mail},201
    else :
        logging.warning("An error occured while updating email of user " + str(user_id))
        return {"message": "Unknown error while updating email"}, 500

#PUT /update/username
@require_valid_user
def update_username(user_id,body):
    username = utils.sanitize_input(body["username"].strip())
    if not username:
        return {"message": "generic_errors.missing_params"}, 400
    userDb = UserDB()
    if len(username) > 250:
        return {"message": "Username is too long"}, 400
    already_existing_user = userDb.getByUsername(username)
    if already_existing_user:
        if already_existing_user.id == user_id:
            return {"message":username},201
        else:
            return {"message": "generic_errors.username_exists"}, 409
    user = userDb.update_username(user_id=user_id, username=username)
    if user:
        return {"message":user.username},201
    else :
        logging.warning("An error occured while updating username of user " + str(user_id))
        return {"message": "Unknown error while updating username"}, 500
   
#PUT /update/vault 
@require_valid_user
def update_vault(user_id, body):
    returnJson = {"message": "Internal server error", "hashing":-1, "totp":-1, "user":-1, "zke":-1}
    try:
        newPassphrase = body["new_passphrase"].strip()
        old_passphrase = body["old_passphrase"].strip()
        enc_vault = body["enc_vault"].strip()
        enc_vault = json.loads(enc_vault)
        zke_key = body["zke_enc"].strip()
        passphrase_salt = body["passphrase_salt"].strip()
        derivedKeySalt = body["derived_key_salt"].strip()
    except Exception as e:
        logging.error(e)
        return '{"message": "Invalid request"}', 400

    if not newPassphrase or not old_passphrase or not zke_key or not passphrase_salt or not derivedKeySalt:
        return {"message": "Missing parameters"}, 400
    
    
    
    is_vault_valid, vault_validation_msg = utils.unsafe_json_vault_validation(enc_vault)
    if not is_vault_valid:
        return {"message": vault_validation_msg}, 400
    userDb = UserDB()
    zke_db = ZKE_DB()
    totp_secretDB = TOTP_secretDB()

    user = userDb.getById(user_id)
    bcrypt = Bcrypt(old_passphrase)
    if not bcrypt.checkpw(user.password):
        logging.info("User " + str(user_id) + " tried to update his vault but provided passphrase is wrong.")
        return {"message": "Invalid passphrase"}, 403
    bcrypt = Bcrypt(newPassphrase)
    try :
        hashedpw = bcrypt.hashpw()
    except ValueError as e:
        logging.warning(e)
        return {"message": "passphrase too long. It must be <70 char"}, 400
    except Exception as e:
        logging.warning("Uknown error occured while hashing password" + str(e))
        returnJson["hashing"]=0
        return returnJson, 500

    logging.info(f"User {user_id} is updating their passphrase. Old passphrase is verified. Proceeding with vault update. IP : {utils.get_ip(request)}")
    
    old_vault = TOTP_secretDB().get_all_enc_secret_by_user_id(user_id)
    if len(old_vault) != len(enc_vault):
        logging.warning(f"User {user_id} tried to update his vault but the number of secrets in the new vault is different from the old one. The update is rejected.")
        return {"message": "To avoid the loss of your information, Zero-TOTP is rejecting this request because it has detected that you might lose data. Please contact quickly Zero-TOTP developers to fix issue."}, 400
    for secret in old_vault:
        if secret.uuid not in enc_vault:
            logging.warning(f"FORBIDDEN. The user {user_id} tried to update but the secret {secret.uuid} is missing in the new vault. The update is rejected.")
            return {"message": "Forbidden action. Zero-TOTP detected that you were updating object you don't have access to. The request is rejected."}, 403
    

    returnJson["hashing"]=1
    errors = 0
    for secret in enc_vault.keys():
        totp = totp_secretDB.get_enc_secret_of_user_by_uuid(user_id, secret)
        if not totp:
            totp = totp_secretDB.add(user_id=user_id, enc_secret=enc_vault[secret], uuid=secret)
            if not totp:
                logging.warning("Unknown error while adding encrypted secret for user " + str(user_id))
                errors = 1
        else:
            if totp.user_id != user_id:
                logging.warning("User " + str(user_id) + " tried to update secret " + str(secret) + " which is not his")
                errors = 1
            else :
                totp = totp_secretDB.update_secret(uuid=secret, enc_secret=enc_vault[secret], user_id=user_id)
                if totp == None:
                    logging.warning("User " + str(user_id) + " tried to update secret " + str(secret) + " but an error occurred server side while storing your  encrypted secret")
                    errors = 1
    zke = zke_db.update(user_id, zke_key)
    userUpdated = userDb.update(user_id=user_id, passphrase=hashedpw, passphrase_salt=passphrase_salt, derivedKeySalt=derivedKeySalt)
    returnJson["totp"]=1 if errors == 0 else 0
    returnJson["user"]=1 if userUpdated else 0
    returnJson["zke"]=1 if zke else 0
    if errors == 0 and userUpdated and zke:
        try:
            ip = utils.get_ip(request)
            thread = threading.Thread(target=utils.send_information_email,args=(ip, user.mail, "Your vault passphrase has been updated"))
            thread.start()
        except Exception as e:
            logging.error("Unknown error while sending information email" + str(e))
        logging.info(f"User {user_id} has successfully updated their vault and passphrase.")
        return {"message": "Vault updated"}, 201
    else:
        logging.warning("An error occured while updating passphrase of user " + str(user_id))
        return returnJson, 500


@require_valid_user
def export_vault(user_id):
    
    vault = {"version":1, "date": str(datetime.datetime.utcnow())}
    user = UserDB().getById(user_id=user_id)
    zkeKey = ZKE_DB().getByUserId(user_id=user_id)
    totp_secrets_list = TOTP_secretDB().get_all_enc_secret_by_user_id(user_id=user_id)
    if not user or not zkeKey:
        return {"message" : "User not found"}, 404
    
    vault["derived_key_salt"] = user.derivedKeySalt
    vault["zke_key_enc"] = zkeKey.ZKE_key
    secrets = utils.get_all_secrets_sorted(totp_secrets_list)
    vault["secrets"] = secrets
    vault["secrets_sha256sum"] = sha256(json.dumps(vault["secrets"],  sort_keys=True).encode("utf-8")).hexdigest()
    vault_b64 = base64.b64encode(json.dumps(vault).encode("utf-8")).decode("utf-8")
    signature = API_signature().sign_rsa(vault_b64)
    vault = vault_b64 + "," + signature
    return vault, 200

# GET /role
@require_userid
def get_role(user_id, *args, **kwargs):
    user = UserDB().getById(user_id=user_id)
    if not user:
        return {"message" : "User not found"}, 404
    elif not user.isVerified and conf.features.emails.require_email_validation:
        return {"role" : "not_verified"}, 200
    return {"role": user.role}, 200


    
# GET /google-drive/oauth/authorization-flow
def get_authorization_flow():
    if not conf.features.google_drive.enabled:
        return {"message": "Oauth is disabled on this tenant. Contact the tenant administrator to enable it."}, 403 
    authorization_url, state = oauth_flow.get_authorization_url()
    flask.session["state"] = state
    logging.info("State stored in session : " + str(state))
    return {"authorization_url": authorization_url, "state":state}, 200

# GET /google-drive/oauth/callback
@require_valid_user
def oauth_callback(user_id):
    if not conf.features.google_drive.enabled:
        return {"message": "Oauth is disabled on this tenant. Contact the tenant administrator to enable it."}, 403
    frontend_URI = conf.environment.frontend_URI
    try: 
        credentials = oauth_flow.get_credentials(request.url, flask.session["state"])

        if credentials == None:
            response = make_response(redirect(frontend_URI + "/oauth/callback?status=error&state="+str(flask.session["state"]),  code=302))
            flask.session.pop("state")
            return response

        response = make_response(redirect(frontend_URI + "/oauth/callback?status=success&state="+str(flask.session["state"]),    code=302))
        creds_b64 = base64.b64encode(json.dumps(credentials).encode("utf-8")).decode("utf-8")
        sse = ServiceSideEncryption()
        encrypted_cipher = sse.encrypt(creds_b64)
        expires_at = int(datetime.datetime.strptime(credentials["expiry"], "%Y-%m-%d %H:%M:%S.%f").timestamp())
        token_db = Oauth_tokens_db()
        tokens = token_db.get_by_user_id(user_id)
        if tokens:
            tokens = token_db.update(user_id=user_id, enc_credentials=encrypted_cipher["ciphertext"] ,expires_at=expires_at, nonce=encrypted_cipher["nonce"], tag=encrypted_cipher["tag"])
        else:
            tokens = token_db.add(user_id=user_id, enc_credentials=encrypted_cipher["ciphertext"], expires_at=expires_at, nonce=encrypted_cipher["nonce"], tag=encrypted_cipher["tag"])
        if tokens:
            google_drive_int = GoogleDriveIntegrationDB()
            integration = google_drive_int.get_by_user_id(user_id)
            if integration == None:
                google_drive_int.create(user_id=user_id, google_drive_sync=1)
            else :
                google_drive_int.update_google_drive_sync(user_id=user_id, google_drive_sync=1)
            flask.session.pop("state")
            return response
        else:
            logging.warning("Unknown error while storing encrypted tokens for user " + str(user_id))
            response = make_response(redirect(frontend_URI + "/oauth/callback?status=error&state="+flask.session.get('state'),  code=302))
            flask.session.pop("state")
            return response
    except oauth_flow.NoRefreshTokenError as e:
        logging.warning(f"Oauth callback for user {user_id} failed because no refresh token was provided.")
        return make_response(redirect(frontend_URI + "/oauth/callback?status=refresh-token-error&state=none",  code=302))
    except Exception as e:
        logging.error("Error while exchanging the authorization code " + str(e))
        logging.error(traceback.format_exc())
        if flask.session.get("state"):
            response = make_response(redirect(frontend_URI + "/oauth/callback?status=error&state="+flask.session.get('state'),  code=302))
            flask.session.pop("state")
        else :
            response = make_response(redirect(frontend_URI + "/oauth/callback?status=error&state=none",  code=302))
        return response



#GET /google-drive/option
@require_valid_user
def get_google_drive_option(user_id):
    if not conf.features.google_drive.enabled:
        return {"message": "Google drive sync is not enabled on this tenant."}, 403
    google_drive_integrations = GoogleDriveIntegrationDB()
    status = google_drive_integrations.is_google_drive_enabled(user_id)
    if status:
        return {"status": "enabled"}, 200
    else:
        return {"status": "disabled"}, 200
    
#PUT /google-drive/backup
@require_valid_user
def backup_to_google_drive(user_id, *args, **kwargs):
    if not conf.features.google_drive.enabled:
        return {"message": "Google drive sync is not enabled on this tenant."}, 403
    
    token_db = Oauth_tokens_db()
    oauth_tokens = token_db.get_by_user_id(user_id)
    google_drive_integrations = GoogleDriveIntegrationDB()

    if not oauth_tokens or not google_drive_integrations.is_google_drive_enabled(user_id):
        return {"message": "Google drive sync is not enabled"}, 403
    sse = ServiceSideEncryption()
    creds_b64 = sse.decrypt( ciphertext=oauth_tokens.enc_credentials, nonce=oauth_tokens.cipher_nonce, tag=oauth_tokens.cipher_tag)
    if creds_b64 == None:
        logging.warning("Error while decrypting credentials for user " + str(user_id))
        return {"message": "Error while decrypting credentials"}, 500
    credentials = json.loads(base64.b64decode(creds_b64).decode("utf-8"))
    try:
        exported_vault,_ = export_vault(user=user_id, context_={"user":user_id}, token_info={"user":user_id})
        google_drive_api.backup(credentials=credentials, vault=exported_vault)
        google_drive_api.clean_backup_retention(credentials=credentials, user_id=user_id)
        return {"message": "Backup done"}, 201
    except Exception as e:
        logging.error("Error while backing up to google drive " + str(e))
        return {"message": "Error while backing up to google drive"}, 500


# GET /google-drive/last-backup/verify
@require_valid_user
def verify_last_backup(user_id):
    if not conf.features.google_drive.enabled:
        return {"message": "Google drive sync is not enabled on this tenant."}, 403
    token_db = Oauth_tokens_db()
    oauth_tokens = token_db.get_by_user_id(user_id)
    google_drive_integrations = GoogleDriveIntegrationDB()
    if not oauth_tokens or not google_drive_integrations.is_google_drive_enabled(user_id):
        return {"message": "Google drive sync is not enabled"}, 403
    sse = ServiceSideEncryption()
    creds_b64 = sse.decrypt( ciphertext=oauth_tokens.enc_credentials, nonce=oauth_tokens.cipher_nonce, tag=oauth_tokens.cipher_tag)
    if creds_b64 == None:
        logging.error("Error while decrypting credentials for user " + str(user_id) + ". creds_b64 = " + str(creds_b64))
        return {"error": "Error while connecting to the Google API"}, 500
    
    
    credentials = json.loads(base64.b64decode(creds_b64).decode("utf-8"))
    if credentials.get("refresh_token") is None:
        logging.warning(f"User {user_id} tried to verify last backup but no refresh token was found in the credentials. This is a blocking error.")
        return {"message": "Error while connecting to the Google API", "error_id": "3c071611-744a-4c93-95c8-c87ee3fce00d"}, 400
    try:
        last_backup_checksum, last_backup_date = google_drive_api.get_last_backup_checksum(credentials)
    except utils.CorruptedFile as e:
        logging.warning("Error while getting last backup checksum " + str(e))
        return {"status": "corrupted_file"}, 200
    except utils.FileNotFound as e:
        logging.warning("Error while getting last backup checksum " + str(e))
        return {"error": "file_not_found"}, 404
    totp_secrets_list = TOTP_secretDB().get_all_enc_secret_by_user_id(user_id=user_id)
    secrets = utils.get_all_secrets_sorted(totp_secrets_list)
    sha256sum = sha256(json.dumps(secrets,  sort_keys=True).encode("utf-8")).hexdigest()
    if last_backup_checksum == sha256sum:
        google_drive_api.clean_backup_retention(credentials=credentials, user_id=user_id)
        return {"status": "ok", "is_up_to_date": True, "last_backup_date": last_backup_date }, 200
    else:
        return {"status": "ok", "is_up_to_date": False, "last_backup_date": "" }, 200


# DELETE /google-drive/option
@require_valid_user
def delete_google_drive_option(user_id):
    if not conf.features.google_drive.enabled:
        return {"message": "Google drive sync is not enabled on this tenant."}, 403
    google_integration = GoogleDriveIntegrationDB()
    token_db = Oauth_tokens_db()
    oauth_tokens = token_db.get_by_user_id(user_id)
    
    if google_integration.get_by_user_id(user_id) is None:
        google_integration.create(user_id, 0)
    if not oauth_tokens:
        GoogleDriveIntegrationDB().update_google_drive_sync(user_id, 0)
        return {"message": "Google drive sync is not enabled"}, 200
    sse = ServiceSideEncryption()
    try:
        creds_b64 = sse.decrypt( ciphertext=oauth_tokens.enc_credentials, nonce=oauth_tokens.cipher_nonce,  tag=oauth_tokens.cipher_tag)
        if creds_b64 == None:
            token_db.delete(user_id)
            GoogleDriveIntegrationDB().update_google_drive_sync(user_id, 0)
            return {"message": "Error while decrypting credentials"}, 200
        credentials = json.loads(base64.b64decode(creds_b64).decode("utf-8"))
        google_drive_api.revoke_credentials(credentials)
        token_db.delete(user_id)
        GoogleDriveIntegrationDB().update_google_drive_sync(user_id, 0)
        return {"message": "Google drive sync disabled"}, 200
    except Exception as e:
        logging.error("Error while deleting backup from google drive " + str(e))
        token_db.delete(user_id)
        GoogleDriveIntegrationDB().update_google_drive_sync(user_id, 0)
        return {"message": "Error while revoking credentials"}, 200

@require_valid_user
def get_preferences(user_id,fields):
    valid_fields = [ "favicon_policy", "derivation_iteration", "backup_lifetime", "backup_minimum", "autolock_delay"]
    all_field = fields == "all" 
    fields_asked = []
    if not all_field:
        fields = fields.split(",")
        for field in fields:
            if field not in fields_asked:
                for valid_field in valid_fields:
                    if field == valid_field:
                        fields_asked.append(valid_field)

        if len(fields_asked) == 0:
            return {"message": "Invalid request"}, 400
    
    user_preferences = {}
    preferences_db = PreferencesDB()
    preferences = preferences_db.get_preferences_by_user_id(user_id)
    if "favicon_policy" in fields_asked or all_field:
        user_preferences["favicon_policy"] = preferences.favicon_preview_policy
    if  "derivation_iteration" in fields_asked or all_field:
        user_preferences["derivation_iteration"] = preferences.derivation_iteration
    if "backup_lifetime" in fields_asked or all_field:
        user_preferences["backup_lifetime"] = preferences.backup_lifetime
    if "backup_minimum" in fields_asked or all_field:
        user_preferences["backup_minimum"] = preferences.minimum_backup_kept
    if "autolock_delay" in fields_asked or all_field:
        user_preferences["autolock_delay"] = preferences.vault_autolock_delay_min
    return user_preferences, 200


@require_valid_user
def set_preference(user_id, body):
    field = body["id"]
    value = body["value"]
    
    valid_fields = [ "favicon_policy", "derivation_iteration", "backup_lifetime", "backup_minimum", "autolock_delay"]
    if field not in valid_fields:
        return {"message": "Invalid request"}, 400
    preferences_db = PreferencesDB()
    if field == "favicon_policy":
        if value not in ["always", "never", "enabledOnly"]:
            return {"message": "Invalid request"}, 400
        preferences = preferences_db.update_favicon(user_id, value)
        if preferences:
            return {"message": "Preference updated"}, 201
        else:# pragma: no cover
            return {"message": "Unknown error while updating preference"}, 500
    elif field == "derivation_iteration":
        try:
            value = int(value)
        except:
            return {"message": "Invalid request"}, 400
        if value < 1000 or value > 1000000:
            return {"message": "iteration must be between 1000 and 1000000 "}, 400
        preferences = preferences_db.update_derivation_iteration(user_id, value)
        if preferences:
            return {"message": "Preference updated"}, 201
        else:# pragma: no cover
            return {"message": "Unknown error while updating preference"}, 500
    elif field == "backup_lifetime":
        try:
            value = int(value)
        except:
            return {"message": "Invalid request"}, 400
        if value < 1 :
            return {"message": "backup lifetime must be at least day"}, 400
        preferences = preferences_db.update_backup_lifetime(user_id, value)
        if preferences:
            return {"message": "Preference updated"}, 201
        else:# pragma: no cover
            return {"message": "Unknown error while updating preference"}, 500
    elif field == "backup_minimum":
        try:
            value = int(value)
        except:
            return {"message": "Invalid request"}, 400
        if value < 1 :
            return {"message": "minimum backup kept must be at least of 1"}, 400
        preferences = preferences_db.update_minimum_backup_kept(user_id, value)
        if preferences:
            return {"message": "Preference updated"}, 201
        else:# pragma: no cover
            return {"message": "Unknown error while updating preference"}, 500
    elif field == "autolock_delay":
        minimum_delay = 1
        maximum_delay = conf.api.refresh_token_validity/60 # autolock is limited by the ability to refresh the token
        try:
            value = int(value)
        except:
            return {"message": "Invalid request"}, 400
        if value < 1 or value > maximum_delay:
            return {"message": "invalid_duration", "minimum_duration_min":minimum_delay, "maximum_duration_min": maximum_delay}, 400
        preferences = preferences_db.update_autolock_delay(user_id, value)
        if preferences:# pragma: no cover
            return {"message": "Preference updated"}, 201
        return {"message": "Unknown error while updating preference"}, 500
    else: # pragma: no cover
        return {"message": "Invalid request"}, 400

# DELETE /google-drive/backup
@require_valid_user
def delete_google_drive_backup(user_id):
    if not conf.features.google_drive.enabled:
        return {"message": "Google drive sync is not enabled on this tenant."}, 403
    google_integration = GoogleDriveIntegrationDB()
    token_db = Oauth_tokens_db()
    oauth_tokens = token_db.get_by_user_id(user_id)
    google_drive_option =google_integration.get_by_user_id(user_id) 
    if google_drive_option == None:
        return {"message": "Google drive sync is not enabled"}, 403
    if google_drive_option.isEnabled == 0:
        return {"message": "Google drive sync is not enabled"}, 403
    if not oauth_tokens:
        return {"message": "Google drive sync is not enabled"}, 403
    sse = ServiceSideEncryption()
    try:
        creds_b64 = sse.decrypt( ciphertext=oauth_tokens.enc_credentials, nonce=oauth_tokens.cipher_nonce,  tag=oauth_tokens.cipher_tag)
        credentials = json.loads(base64.b64decode(creds_b64).decode("utf-8"))
        status = google_drive_api.delete_all_backups(credentials=credentials)
        if status :
            return {"message": "Backups deleted"}, 200
        else:
            return {"message": "Error while deleting backups"}, 500
    except Exception as e:
        logging.error("Error while deleting backup from google drive " + str(e))
        token_db.delete(user_id)
        GoogleDriveIntegrationDB().update_google_drive_sync(user_id, 0)
        return {"message": "Error while deleting backups"}, 500
    

@require_passphrase_verification
def delete_account(user_id):
    logging.info("Deleting account for user " + str(user_id))
    user_obj = UserDB().getById(user_id)
    if user_obj.role == "admin":
        return {"message": "Admin cannot be deleted"}, 403
    try: # we try to delete the user backups if possible. If not, this is not a blocking error.
        context = {"user": user_id}
        delete_google_drive_backup(context, user_id, context)
        delete_google_drive_option(context, user_id, context)
    except Exception as e:
        logging.warning("Error while deleting backups for user " + str(user_id) + ". Exception : " + str(e))
    try:
        UserDB().delete(user_id)
        logging.info("Account deleted for user " + str(user_id))
        return {"message": "Account deleted"}, 200
    except Exception as e:
        logging.warning("Error while deleting user from database for user " + str(user_id) + ". Exception : " + str(e))
        return {"message": "Error while deleting account"}, 500
    
    


@require_userid
def send_verification_email(user_id):
    if not conf.features.emails.require_email_validation:
        return {"message": "not implemented"}, 501
    rate_limiting = Rate_Limiting_DB()
    if(rate_limiting.is_send_verification_email_rate_limited(user_id=user_id)):
            return {"message": "Rate limited",  'ban_time':conf.features.rate_limiting.email_ban_time}, 429
    logging.info("Sending verification email to user " + str(user_id))
    user = UserDB().getById(user_id)
    if user == None:
        return {"message": "User not found"}, 404
    token = utils.generate_new_email_verification_token(user_id=user_id)
    try:
        send_email.send_verification_email(user.mail, token)
        logging.info("Verification email sent to user " + str(user_id))
        ip = utils.get_ip(request=request)
        rate_limiting.add_send_verification_email(ip=ip, user_id=user_id)
        return {"message": "Verification email sent"}, 200
    except Exception as e:
        logging.error("Error while sending verification email to user " + str(user_id) + ". Exception : " + str(e))
        return {"message": "Error while sending verification email"}, 500

@require_userid
def verify_email(user_id,body):
    user = UserDB().getById(user_id)
    if user == None:
        return {"message": "generic_errors.user_not_found"}, 404
    if user.isVerified:
        return {"message": "email_verif.error.already_verified"}, 200
    token_db = EmailVerificationToken_db()
    token_obj = token_db.get_by_user_id(user_id)
    if token_obj == None:
        return {"message": "email_verif.error.no_active_code"}, 403
    if datetime.datetime.now(tz=datetime.timezone.utc).timestamp() > float(token_obj.expiration) :
        token_db.delete(user_id)
        return {"message": "email_verif.error.expired"}, 403
    if int(token_obj.failed_attempts >= 5):
        logging.warning("User " + str(user_id) + " denied verification because of too many failed attempts.")
        return {"message":  "email_verif.error.too_many_failed"}, 403
    if token_obj.token != body["token"]:
        token_db.increase_fail_attempts(user_id)
        logging.warning("User " + str(user_id) + " tried to verify email with wrong token.")
        return {"message": "email_verif.error.failed", "attempt_left":5-(int(token_obj.failed_attempts))}, 403
    token_db.delete(user_id)
    Rate_Limiting_DB().flush_email_verification_limit(user_id)
    user = UserDB().update_email_verification(user_id, True)
    if user:
        return {"message": "Email verified"}, 200
    else:# pragma: no cover
        return {"message": "Error while verifying email"}, 500


@require_valid_user
def get_whoami(user_id):
    user = UserDB().getById(user_id)
    return {"username": user.username, "email": user.mail, "id":user_id}, 200


def get_global_notification():
    notif = Notifications_db().get_last_active_notification()
    if notif is None : 
        return {"display_notification":False}
    if notif.authenticated_user_only:
        return {"display_notification": True, "authenticated_user_only": True}
    else:
        return {
            "display_notification": True, 
            "authenticated_user_only": False,
            "message":notif.message,
            "timestamp":float(notif.timestamp)
        }
    
    
@require_valid_user
def get_internal_notification(user_id):
    notif = Notifications_db().get_last_active_notification()
    if notif is None : 
        return {"display_notification":False}
    
    return {
            "display_notification": True, 
            "authenticated_user_only": False,
            "message":notif.message,
            "timestamp":float(notif.timestamp)
        }


# PUT /auth/refresh
@ip_rate_limit
def auth_refresh_token(ip, *args, **kwargs):
    session_token_cookie = request.cookies.get("session-token")
    refresh_token_cookie = request.cookies.get("refresh-token")
    rate_limiting = Rate_Limiting_DB()
    if not session_token_cookie or not refresh_token_cookie:
        rate_limiting.add_failed_login(ip)
        return {"message": "Missing token"}, 401
    session_token = SessionTokenRepo().get_session_token(session_token_cookie)
    if not session_token:
        rate_limiting.add_failed_login(ip)
        return {"message": "Invalid token"}, 401
    if session_token.revoke_timestamp is not None:
        rate_limiting.add_failed_login(ip)
        return {"message": "Token revoked"}, 401
    refresh_token = RefreshToken_db().get_refresh_token_by_hash(sha256(refresh_token_cookie.encode("utf-8")).hexdigest())
    if not refresh_token:
        rate_limiting.add_failed_login(ip, user_id=session_token.user_id)
        logging.warning(f"Session of user {session_token.user_id} tried to be refreshed with an refresh token (not present in the db)")
        return {"message": "Access denied"}, 403
    new_session_token, new_refresh_token = refresh_token_func.refresh_token_flow(refresh_token=refresh_token, session_token=session_token, ip=ip)
    response = Response(status=200, mimetype="application/json", response=json.dumps({"challenge":"ok"}))
    response.set_auth_cookies(new_session_token, new_refresh_token)
    return response

# GET /healthcheck
def health_check():
    health_status = {}
    global_healthy = True
    if conf.api.node_check_enabled:
        health_status["node"] = hmac.new(conf.api.node_name_hmac_secret.encode('utf-8'), conf.api.node_name.encode('utf-8'), hashlib.sha256).hexdigest()
    
    try:
        db.session.execute(text('SELECT 1'))
        health_status["database"] = "OK"
    except Exception as e:
        logging.warning("Database healthcheck failed : " + str(e))
        health_status["database"] = "NOT OK"
        global_healthy = False
    health_status["version"] = conf.api.version
    health_status["build"] = conf.api.build

    health_status["health"] = "OK" if global_healthy else "NOT OK"
    http_status = 200 if global_healthy else 500
    
    return health_status, http_status
    

# GET /vault/signature/public-key
def get_public_key():
    with open(conf.api.public_key_path, "r") as f:
        public_key = f.read()
    if ServerRSAKeys().validate_rsa_public_key(public_key):
        return {"public_key": public_key}, 200
    else:
        logging.error("This is a critical error from get_public_key(). A public key has been requested but the key is not valid. An error as been returned to the user.")
        return {"message": "Invalid"}, 403
    
