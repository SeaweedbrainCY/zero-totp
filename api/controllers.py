from flask import request, Response, redirect, make_response
import flask
import connexion
import json
from database.user_repo import User as UserDB
from database.zke_repo import ZKE as ZKE_DB
from database.totp_secret_repo import TOTP_secret as TOTP_secretDB
from CryptoClasses.hash_func import Bcrypt
from database.oauth_tokens_repo import Oauth_tokens as Oauth_tokens_db
from CryptoClasses.hash_func import Bcrypt
from Oauth import google_drive_api
import logging
import environment as env
import random
import string
import CryptoClasses.jwt_func as jwt_auth
import CryptoClasses.sign_func as api_signature
import CryptoClasses.jwt_func as jwt_auth
import Oauth.oauth_flow as oauth_flow
import Utils.utils as utils
import os
import base64
import datetime
from datetime import timedelta



if env.environment == "development":
    logging.getLogger().setLevel(logging.INFO)


# POST /signup
def signup():
    dataJSON = json.dumps(request.get_json())
    try:
        data = json.loads(dataJSON)
        username = utils.escape(data["username"].strip())
        passphrase = data["password"].strip()
        email = utils.escape(data["email"].strip())
        derivedKeySalt = utils.escape(data["derivedKeySalt"].strip())
        zke_key = utils.escape(data["ZKE_key"].strip())
        passphraseSalt = utils.escape(data["passphraseSalt"].strip())
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
    
    if not username or not passphrase or not email or not derivedKeySalt or not zke_key or not passphraseSalt:
        return {"message": "Missing parameters"}, 400
    if(not utils.check_email(email) or not utils.check_username(username) or not utils.check_password(passphrase)):
        return {"message": "Forbidden parameters"}, 403
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
        user = userDB.create(username, email, hashedpw, derivedKeySalt, 0, passphraseSalt)
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
        email = utils.escape(data["email"]).strip()
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
    
    if not passphrase or not email:
        return {"message": "Missing parameters"}, 400
    if(not utils.check_email(email) or not utils.check_password(passphrase)):
        return {"message": "Forbidden parameters"}, 403
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

    response = Response(status=200, mimetype="application/json", response=json.dumps({"username": user.username, "id":user.id, "derivedKeySalt":user.derivedKeySalt, "isGoogleDriveSync": user.googleDriveSync}))
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
def get_encrypted_secret(uuid):
    try:
        user_id = connexion.context.get("user")
        logging.info(connexion.context)
        if user_id == None:
            return {"message": "Unauthorized"}, 401
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
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
def add_encrypted_secret(uuid):
    try:
        user_id = connexion.context.get("user")
        logging.info(connexion.context)
        if user_id == None:
            return {"message": "Unauthorized"}, 401
        dataJSON = json.dumps(request.get_json())
        data = json.loads(dataJSON)
        enc_secret = utils.escape(data["enc_secret"]).strip()
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
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
def update_encrypted_secret(uuid):
    try:
        user_id = connexion.context.get("user")
        logging.info(connexion.context)
        if user_id == None:
            return {"message": "Unauthorized"}, 401
        dataJSON = json.dumps(request.get_json())
        data = json.loads(dataJSON)
        enc_secret = utils.escape(data["enc_secret"]).strip()
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
    
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
def delete_encrypted_secret(uuid):
    try:
        user_id = connexion.context.get("user")
        logging.info(connexion.context)
        if user_id == None:
            return {"message": "Unauthorized"}, 401
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
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
def get_all_secrets():
    try:
        user_id = connexion.context.get("user")
        logging.info(connexion.context)
        if user_id == None:
            return {"message": "Unauthorized"}, 401
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
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
def get_ZKE_encrypted_key():
    try:
        user_id = connexion.context.get("user")
        zke_db = ZKE_DB()
        zke_key = zke_db.getByUserId(user_id)
        if zke_key:
                return {"zke_encrypted_key": zke_key.ZKE_key}, 200
        else:
            return {"message": "No ZKE key found for this user"}, 404
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400



#PUT /email
def update_email():
    user_id = connexion.context.get("user")
    if user_id == None:
        return {"message": "Unauthorized"}, 401
    dataJSON = json.dumps(request.get_json())
    data = json.loads(dataJSON)
    email = utils.escape(data["email"]).strip()
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
def update_vault():
    returnJson = {"message": "Internal server error", "hashing":-1, "totp":-1, "user":-1, "zke":-1}
    try:
        user_id = connexion.context.get("user")
        if user_id == None:
            return {"message": "Unauthorized"}, 401
        dataJSON = json.dumps(request.get_json())
        data = json.loads(dataJSON)
        newPassphrase = data["new_passphrase"].strip()
        old_passphrase = data["old_passphrase"].strip()
        enc_vault = data["enc_vault"].strip()
        enc_vault = json.loads(enc_vault)
        zke_key = data["zke_enc"].strip()
        passphrase_salt = data["passphrase_salt"].strip()
        derivedKeySalt = data["derived_key_salt"].strip()
    except:
        return '{"message": "Invalid request"}', 400

    if not newPassphrase or not old_passphrase or not enc_vault or not zke_key or not passphrase_salt or not derivedKeySalt:
        return {"message": "Missing parameters"}, 400
    
    if not utils.check_password(newPassphrase):
        return {"message": "Bad passphrase format"}, 400
    
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



def export_vault():
    try:
        user_id = connexion.context.get("user")
    except:
        return {"message": "Invalid request"}, 400
    
    vault = {"version":1, "date": str(datetime.datetime.utcnow())}
    user = UserDB().getById(user_id=user_id)
    zkeKey = ZKE_DB().getByUserId(user_id=user_id)
    totp_secrets_list = TOTP_secretDB().get_all_enc_secret_by_user_id(user_id=user_id)
    if not user or not zkeKey:
        return {"message" : "User not found"}, 404
    
    vault["derived_key_salt"] = user.derivedKeySalt
    vault["zke_key_enc"] = zkeKey.ZKE_key
    secrets = []
    for secret in totp_secrets_list:
        secrets.append({"uuid": secret.uuid, "enc_secret": secret.secret_enc})
    vault["secrets"] = secrets
    vault_b64 = base64.b64encode(json.dumps(vault).encode("utf-8")).decode("utf-8")
    signature = api_signature.sign(vault_b64)
    vault = vault_b64 + "," + signature
    return vault, 200

    
# GET /google-drive/oauth/authorization_flow
def get_authorization_flow():
    authorization_url, state = oauth_flow.get_authorization_url()
    flask.session["state"] = state
    logging.info("State stored in session : " + str(state))
    return {"authorization_url": authorization_url, "state":state}, 200

# GET /google-drive/oauth/callback
def oauth_callback():
    try: 
        credentials = oauth_flow.get_credentials(request.url, flask.session["state"])

        if credentials == None:
            response = make_response(redirect(env.frontend_URI + "/oauth/callback?status=error&state="+flask.session["state"],  code=302))
            flask.session.pop("state")
            return response

        response = make_response(redirect(env.frontend_URI + "/oauth/callback?status=success&state="+flask.session["state"],    code=302))
        flask.session.pop("state")
        creds_b64 = base64.b64encode(json.dumps(credentials).encode("utf-8")).decode("utf-8")
        response.set_cookie("credentials", creds_b64, httponly=False, secure=True, samesite="Strict", max_age=timedelta(minutes=2))
        return response
    except Exception as e:
        logging.error("Error while exchanging the authorization code " + str(e))
        if flask.session.get("state"):
            response = make_response(redirect(env.frontend_URI + "/oauth/callback?status=error&state="+flask.session.get('state'),  code=302))
            flask.session.pop("state")
        else :
            response = make_response(redirect(env.frontend_URI + "/oauth/callback?status=error&state=none",  code=302))
        return response

# GET  /google-drive/oauth/enc-credentials:
def get_encrypted_creds():
    try:
        user_id = connexion.context.get("user")
        if user_id == None:
            return {"message": "Unauthorized"}, 401
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
    oauth_db = Oauth_tokens_db()
    oauth = oauth_db.get_by_user_id(user_id)
    if oauth:
        return {"enc_credentials": oauth.enc_credentials}, 200
    else:
        return {"message": "No encrypted credentials found"}, 404



# POST  /google-drive/oauth/enc-credentials:
def set_encrypted_credentials():
    try:
        user_id = connexion.context.get("user")
        if user_id == None:
            return {"message": "Unauthorized"}, 401
        dataJSON = json.dumps(request.get_json())
        data = json.loads(dataJSON)
        enc_credentials = utils.escape(data["enc_credentials"]).strip()
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
    if not enc_credentials :
        return {"message": "Missing parameters"}, 400
   
    token_db = Oauth_tokens_db()
    tokens = token_db.get_by_user_id(user_id)
    expires_at = (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).timestamp()
    if tokens:
        tokens = token_db.update(user_id=user_id, enc_credentials=enc_credentials ,expires_at=expires_at)
    else:
        tokens = token_db.add(user_id=user_id, enc_credentials=enc_credentials, expires_at=expires_at)
    if tokens:
        userDB = UserDB()
        userDB.update_google_drive_sync(user_id=user_id, google_drive_sync=1)
        response = Response(status=201, mimetype="application/json", response=json.dumps({"message": "Encrypted tokens stored"}))
        response.set_cookie('credentials', "", expires=0)
        return response
    else:
        logging.warning("Unknown error while storing encrypted tokens for user " + str(user_id))
        return {"message": "Unknown error while storing encrypted tokens"}, 500
    
#GET /google-drive/status
def get_google_drive_option():
    try:
        user_id = connexion.context.get("user")
        if user_id == None:
            return {"message": "Unauthorized"}, 401
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
    token_db = Oauth_tokens_db()
    tokens = token_db.get_by_user_id(user_id)
    if tokens:
        return {"status": "enabled"}, 200
    else:
        return {"status": "disabled"}, 200
    
#PUT /google-drive/backup
def backup_to_google_drive():
    try:
        user_id = connexion.context.get("user")
        if user_id == None:
            return {"message": "Unauthorized"}, 401
        dataJSON = json.dumps(request.get_json())
        data = json.loads(dataJSON)
        token = utils.escape(data["token"]).strip()
        refresh_token = utils.escape(data["refresh_token"]).strip()
        token_uri = utils.escape(data["token_uri"]).strip()
        client_id = utils.escape(data["client_id"]).strip()
        client_secret = utils.escape(data["client_secret"]).strip()
        scopes_unsecure = data["scopes"]
        expiry = utils.escape(data["expiry"]).strip()
        scopes = []
        for scope in scopes_unsecure:
            scopes.append(utils.escape(scope).strip())

    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
    if not token or not refresh_token or not token_uri or not client_id or not client_secret or not scopes:
        return {"message": "Missing parameters"}, 400

    credentials = {
        'token': token,
        'refresh_token': refresh_token,
        'token_uri': token_uri,
        'client_id': client_id,
        'client_secret': client_secret,
        'scopes': scopes,
        'expiry' : expiry}
   # try:
    google_drive_api.backup(credentials=credentials)
    return {"message": "Backup done"}, 201
   # except Exception as e:
   #     logging.error("Error while backing up to google drive " + str(e))
   #     return {"message": "Error while backing up to google drive"}, 500
    
    