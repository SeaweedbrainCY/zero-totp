from flask import request, Response, redirect, make_response
import flask
import connexion
import json
from database.user_repo import User as UserDB
from database.zke_repo import ZKE as ZKE_DB
from database.totp_secret_repo import TOTP_secret as TOTP_secretDB
from database.google_drive_integration_repo import GoogleDriveIntegration as GoogleDriveIntegrationDB
from database.preferences_repo import Preferences as PreferencesDB
from database.admin_repo import Admin as Admin_db
from CryptoClasses.hash_func import Bcrypt
from environment import logging
from database.oauth_tokens_repo import Oauth_tokens as Oauth_tokens_db
from CryptoClasses.hash_func import Bcrypt
from Oauth import google_drive_api
import environment as env
import random
import string
import CryptoClasses.jwt_func as jwt_auth
from CryptoClasses.sign_func import API_signature
import CryptoClasses.jwt_func as jwt_auth
import Oauth.oauth_flow as oauth_flow
import Utils.utils as utils
import os
import base64
import datetime
from Utils.security_wrapper import require_admin_token, require_admin_role, require_userid
import traceback
from hashlib import sha256
from CryptoClasses.encryption import ServiceSideEncryption 
from database.db import db



if env.environment == "development":
    logging.getLogger().setLevel(logging.INFO)


# POST /signup
def signup():
    dataJSON = json.dumps(request.get_json())
    try:
        data = json.loads(dataJSON)
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
    if not utils.check_email(email) :
        return {"message": "Bad email format"}, 401
    userDB = UserDB()
    user = userDB.getByEmail(email)
    if user:
        return {"message": "User already exists"}, 409
    
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
        user = userDB.create(username, email, hashedpw, derivedKeySalt, 0, passphraseSalt, today)
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
            return {"message": "User created"}, 201
        else :
            userDB.delete(user.id)
            logging.error("Unknown error while storing user ZKE keys" + str(username))
            return {"message": "Unknown error while registering user encrypted keys"}, 500
    else :
        logging.error("Unknown error while creating user" + str(username))
        return {"message": "Unknown error while creating user"}, 500



# POST /login
def login():
    dataJSON = json.dumps(request.get_json())
    try:
        data = json.loads(dataJSON)
        passphrase = data["password"].strip()
        email = utils.sanitize_input(data["email"]).strip()
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
    
    if not passphrase or not email:
        return {"message": "Missing parameters"}, 400
    if(not utils.check_email(email) ):
        return {"message": "Bad email format"}, 403
    userDB = UserDB()

    user = userDB.getByEmail(email)
    logging.info(user)
    bcrypt = Bcrypt(passphrase)
    if not user:
        logging.info("User " + str(email) + " tried to login but does not exist. A fake password is checked to avoid timing attacks")
        fakePassword = ''.join(random.choices(string.ascii_letters, k=random.randint(10, 20)))
        bcrypt.checkpw(fakePassword)
        return {"message": "Invalid credentials"}, 403
    checked = bcrypt.checkpw(user.password)
    if not checked:
        return {"message": "Invalid credentials"}, 403
        


    jwt_token = jwt_auth.generate_jwt(user.id)

    response = Response(status=200, mimetype="application/json", response=json.dumps({"username": user.username, "id":user.id, "derivedKeySalt":user.derivedKeySalt, "isGoogleDriveSync": GoogleDriveIntegrationDB().is_google_drive_enabled(user.id), "role":user.role}))
    response.set_cookie("api-key", jwt_token, httponly=True, secure=True, samesite="Lax", max_age=3600)
    return response

#GET /login/specs
def get_login_specs(username):
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
@require_userid
def get_encrypted_secret(user_id, uuid):
    totp_secretDB =  TOTP_secretDB()
    enc_secret = totp_secretDB.get_enc_secret_by_uuid(user_id, uuid)
    if not enc_secret:
        return {"message": "Forbidden"}, 403
    else:
        if enc_secret.user_id == user_id:
            return {"enc_secret": enc_secret.secret_enc}, 200
        else :    
            logging.warning("User " + str(user_id) + " tried to access secret " + str(uuid) + " which is not his")
            return {"message": "Forbidden"}, 403
        
#POST /encrypted_secret/{uuid}
@require_userid
def add_encrypted_secret(user_id,uuid, body):
    enc_secret = utils.sanitize_input(body["enc_secret"]).strip()
    if(uuid == ""):
        return {"message": "Invalid request"}, 400
    totp_secretDB =  TOTP_secretDB()
    if totp_secretDB.get_enc_secret_by_uuid(user_id, uuid):
        return {"message": "Forbidden"}, 403
    else:
        if totp_secretDB.add(user_id, enc_secret, uuid):
            return {"message": "Encrypted secret added"}, 201
        else :
            logging.warning("Unknown error while adding encrypted secret for user " + str(user_id))
            return {"message": "Unknown error while adding encrypted secret"}, 500

#PUT /encrypted_secret/{uuid}
@require_userid
def update_encrypted_secret(user_id,uuid, body):
    enc_secret = body["enc_secret"]
    
    totp_secretDB =  TOTP_secretDB()
    totp = totp_secretDB.get_enc_secret_by_uuid(user_id, uuid)
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
@require_userid
def delete_encrypted_secret(user_id,uuid):
    if(uuid == ""):
        return {"message": "Invalid request"}, 400
    totp_secretDB =  TOTP_secretDB()
    totp = totp_secretDB.get_enc_secret_by_uuid(user_id, uuid)
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
@require_userid
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
@require_userid
def get_ZKE_encrypted_key(user_id):
        logging.info(user_id)
        zke_db = ZKE_DB()
        zke_key = zke_db.getByUserId(user_id)
        if zke_key:
                return {"zke_encrypted_key": zke_key.ZKE_key}, 200
        else:
            return {"message": "No ZKE key found for this user"}, 404



#PUT /email
@require_userid
def update_email(user_id,body):
    email = utils.sanitize_input(body["email"]).strip()
    if not utils.check_email(email):
        return {"message": "Bad email format"}, 400
         
    userDb = UserDB()
    if userDb.getByEmail(email):
        return {"message": "email already used"}, 403
    user = userDb.update_email(user_id=user_id, email=email)
    if user:
        return {"message":user.mail},201
    else :
        logging.warning("An error occured while updating email of user " + str(user_id))
        return {"message": "Unknown error while updating email"}, 500

   
#PUT /update/vault 
@require_userid
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
    except:
        return '{"message": "Invalid request"}', 400

    if not newPassphrase or not old_passphrase or not enc_vault or not zke_key or not passphrase_salt or not derivedKeySalt:
        return {"message": "Missing parameters"}, 400
    
    userDb = UserDB()
    zke_db = ZKE_DB()
    totp_secretDB = TOTP_secretDB()

    user = userDb.getById(user_id)
    bcrypt = Bcrypt(old_passphrase)
    if not bcrypt.checkpw(user.password):
        return {"message": "Invalid passphrase"}, 403
    bcrypt = Bcrypt(newPassphrase)
    try :
        hashedpw = bcrypt.hashpw()
    except ValueError as e:
        logging.debug(e)
        returnJson["hashing"]=0
        return returnJson, 500
    except Exception as e:
        logging.warning("Uknown error occured while hashing password" + str(e))
        returnJson["hashing"]=0
        return returnJson, 500
    
    returnJson["hashing"]=1
    errors = 0
    for secret in enc_vault.keys():
        totp = totp_secretDB.get_enc_secret_by_uuid(user_id, secret)
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
        return {"message": "Vault updated"}, 201
    else:
        logging.warning("An error occured while updating passphrase of user " + str(user_id))
        return returnJson, 500


@require_userid
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

def get_role(token_info, *args, **kwargs):
    user_id = token_info["sub"]
    user = UserDB().getById(user_id=user_id)
    if not user:
        return {"message" : "User not found"}, 404
    return {"role": user.role}, 200


@require_admin_token
def get_users_list(*args, **kwargs):
    users = UserDB().get_all()
    if not users:
        return {"message" : "No user found"}, 404
    users_list = []
    for user in users:
        users_list.append({"username": user.username, "email": user.mail, "role": user.role, "createdAt": user.createdAt, "isBlocked": user.isBlocked})
    return {"users": users_list}, 200


@require_admin_role
def admin_login(user_id, body):
    token = body["token"].strip()
    admin_user = Admin_db().get_by_user_id(user_id)
    
    bcrypt = Bcrypt(token)
    if not admin_user:
        logging.info("User " + str(user_id) + " tried to login as admin but is not an admin. A fake password is checked to avoid timing attacks. It has the admin role but no login token.")
        fake_pass = ''.join(random.choices(string.ascii_letters, k=random.randint(10, 20)))
        bcrypt.checkpw(fake_pass)
        return {"message": "Invalid credentials"}, 403
    checked = bcrypt.checkpw(admin_user.token_hashed)
    print("admin_user expiration", admin_user.token_expiration)
    if not checked:
        logging.info("User " + str(user_id) + " tried to login as admin but provided token is wrong. Connexion rejected.")
        return {"message": "Invalid credentials"}, 403
    if float(admin_user.token_expiration)  < datetime.datetime.utcnow().timestamp():
        logging.info("User " + str(user_id) + " tried to login as admin but provided token is expired. Connexion rejected.")
        return {"message": "Token expired"}, 403
    admin_jwt = jwt_auth.generate_jwt(user_id, admin=True)
    response = Response(status=200, mimetype="application/json", response=json.dumps({"challenge":"ok"}))
    response.set_cookie("admin-api-key", admin_jwt, httponly=True, secure=True, samesite="Lax", max_age=600)
    logging.info("User " + str(user_id) + " logged in as admin")
    return response
    
    
# GET /google-drive/oauth/authorization_flow
def get_authorization_flow():
    authorization_url, state = oauth_flow.get_authorization_url()
    flask.session["state"] = state
    logging.info("State stored in session : " + str(state))
    return {"authorization_url": authorization_url, "state":state}, 200

# GET /google-drive/oauth/callback
@require_userid
def oauth_callback(user_id):
    frontend_URI = env.frontend_URI[0] # keep the default URI, not regionized. 
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
@require_userid
def get_google_drive_option(user_id):
    google_drive_integrations = GoogleDriveIntegrationDB()
    status = google_drive_integrations.is_google_drive_enabled(user_id)
    if status:
        return {"status": "enabled"}, 200
    else:
        return {"status": "disabled"}, 200
    
#PUT /google-drive/backup
@require_userid
def backup_to_google_drive(user_id, *args, **kwargs):
    
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


@require_userid
def verify_last_backup(user_id):
    token_db = Oauth_tokens_db()
    oauth_tokens = token_db.get_by_user_id(user_id)
    google_drive_integrations = GoogleDriveIntegrationDB()
    if not oauth_tokens or not google_drive_integrations.is_google_drive_enabled(user_id):
        return {"message": "Google drive sync is not enabled"}, 403
    sse = ServiceSideEncryption()
    creds_b64 = sse.decrypt( ciphertext=oauth_tokens.enc_credentials, nonce=oauth_tokens.cipher_nonce, tag=oauth_tokens.cipher_tag)
    if creds_b64 == None:
        logging.warning("Error while decrypting credentials for user " + str(user_id) + ". creds_b64 = " + str(creds_b64))
        return {"error": "Error while connecting to the Google API"}, 500
    
    
    credentials = json.loads(base64.b64decode(creds_b64).decode("utf-8"))
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


@require_userid
def delete_google_drive_option(user_id):
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

@require_userid
def get_preferences(user_id,fields):
    valid_fields = [ "favicon_policy", "derivation_iteration", "backup_lifetime", "backup_minimum"]
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
    return user_preferences, 200


@require_userid
def set_preference(user_id, body):
    field = body["id"]
    value = body["value"]
    
    valid_fields = [ "favicon_policy", "derivation_iteration", "backup_lifetime", "backup_minimum"]
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
    else:# pragma: no cover
        return {"message": "Invalid request"}, 400

