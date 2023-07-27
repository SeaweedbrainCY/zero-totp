from flask import request, Response
import connexion
import json
from database.user_repo import User as UserDB
from database.zke_repo import ZKE as ZKE_DB
from database.totp_secret_repo import TOTP_secret as TOTP_secretDB
from Crypto.hash_func import Bcrypt
import logging
import environment as env
import random
import string
import Crypto.jwt_func as jwt_auth



if env.environment == "development":
    logging.getLogger().setLevel(logging.INFO)


# POST /signup
def signup():
    dataJSON = json.dumps(request.get_json())
    try:
        data = json.loads(dataJSON)
        data["username"] = data["username"].strip()
        data["password"] = data["password"].strip()
        data["email"] = data["email"].strip()
        data["salt"] = data["salt"].strip()
        data["ZKE_key"] = data["ZKE_key"].strip()
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
    
    if not data["username"] or not data["password"] or not data["email"]:
        return {"message": "Missing parameters"}, 400
    
    userDB = UserDB()
    user = userDB.getByEmail(data["email"])
    if user:
        return {"message": "User already exists"}, 409
    
    bcrypt = Bcrypt(data["password"])
    try : 
        hashedpw = bcrypt.hashpw()
    except ValueError as e:
        logging.debug(e)
        return {"message": "Password is too long"}, 400
    except Exception as e:
        logging.warning("Uknown error occured while hashing password" + str(e))
        return {"message": "Unknown error while hashing your password"}, 500
    
    randomSalt = data["salt"]
    try:
        user = userDB.create(data["username"], data["email"], hashedpw, randomSalt)
    except Exception as e:
        logging.error("Unknown error while creating user" + str(e))
        return {"message": "Unknown error while creating user"}, 500
    if user :
        try:
            zke_db = ZKE_DB()
            zke_key = zke_db.create(user.id, data["ZKE_key"])
        except Exception as e:
            userDB.delete(user.id)
            logging.error("Unknown error while storing user ZKE keys" + str(e))
            return {"message": "Unknown error while registering user encrypted keys"}, 500
        if zke_key:
            return {"message": "User created"}, 201
        else :

            logging.error("Unknown error while storing user ZKE keys" + str(data["username"]))
            return {"message": "Unknown error while registering user encrypted keys"}, 500
    else :
        logging.error("Unknown error while creating user" + str(data["username"]))
        return {"message": "Unknown error while creating user"}, 500



# POST /login
def login():
    dataJSON = json.dumps(request.get_json())
    try:
        data = json.loads(dataJSON)
        data["password"] = data["password"].strip()
        data["email"] = data["email"].strip()
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
    
    if not data["password"] or not data["email"]:
        return {"message": "Missing parameters"}, 400
    userDB = UserDB()
    user = userDB.getByEmail(data["email"])
    logging.info(user)
    bcrypt = Bcrypt(data["password"])
    if not user:
        #we hash for security reasons
        fakePassword = ''.join(random.choices(string.ascii_letters, k=random.randint(10, 20)))
        bcrypt.checkpw(fakePassword)
        return {"message": "Invalid credentials"}, 403
    checked = bcrypt.checkpw(user.password)
    if not checked:
        return {"message": "Invalid credentials"}, 403
        


    jwt_token = jwt_auth.generate_jwt(user.id)

    response = Response(status=200, mimetype="application/json", response=json.dumps({"username": user.username, "id":user.id, "derivedKeySalt":user.derivedKeySalt}))
    response.set_cookie("api-key", jwt_token, httponly=True, secure=env.isCookieSecure, samesite="Lax", max_age=3600)
    return response
    
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
        enc_secret = data["enc_secret"].strip()
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
    if(uuid == ""):
        return {"message": "Invalid request"}, 400
    totp_secretDB =  TOTP_secretDB()
    if totp_secretDB.get_enc_secret_by_uuid(user_id, uuid):
        return {"message": "Forbidden"}, 403
    else:
        try:
            totp_secretDB.add(user_id, enc_secret, uuid)
        except Exception as e:
            logging.warning("Unknown error while adding encrypted secret for user " + str(user_id) + " : " + str(e))
            return {"message": "Unknown error while adding encrypted secret"}, 500
        return {"message": "Encrypted secret added"}, 201

#PUT /encrypted_secret/{uuid}
def update_encrypted_secret(uuid):
    try:
        user_id = connexion.context.get("user")
        logging.info(connexion.context)
        if user_id == None:
            return {"message": "Unauthorized"}, 401
        dataJSON = json.dumps(request.get_json())
        data = json.loads(dataJSON)
        enc_secret = data["enc_secret"].strip()
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
    
    totp_secretDB =  TOTP_secretDB()
    totp = totp_secretDB.get_enc_secret_by_uuid(user_id, uuid)
    if not totp:
        logging.debug("User " + str(user_id) + " tried to update secret " + str(uuid) + " which does not exist")
        return {"message": "Forbidden"}, 403
    else:
        if totp.user_id != user_id:
            logging.warning("User " + str(user_id) + " tried to update secret " + str(uuid) + " which is not his")
            return {"message": "Forbidden"}, 403
        try:
            totp = totp_secretDB.update_secret(uuid, enc_secret)
            if totp == None:
                logging.warning("User " + str(user_id) + " tried to update secret " + str(uuid) + " which does not exist")
                return {"message": "An error occurred server side while storing your encrypted secret"}, 500
            else:
                return {"message": "Encrypted secret updated"}, 201
        except Exception as e:
            logging.warning("Unknown error while updating encrypted secret for user " + str(user_id) + " : " + str(e))
            return {"message": "Unknown error while updating encrypted secret"}, 500

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
        try:
            totp_secretDB.delete(uuid)
        except Exception as e:
            logging.warning("Unknown error while deleting encrypted secret for user " + str(user_id) + " : " + str(e))
            return {"message": "Unknown error while deleting encrypted secret"}, 500
        return {"message": "Encrypted secret deleted"}, 201

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
        try:
            zke_key = zke_db.getByUserId(user_id)
            if zke_key:
                    return {"zke_encrypted_key": zke_key.ZKE_key}, 200
            else:
                return {"message": "No ZKE key found for this user"}, 404
        except Exception as e:
            logging.warning("Unknown error while fetching ZKE key of user" + str(user_id) + " : " + str(e))
            return {"message": "Unknown error while fetching ZKE key"}, 500
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
   