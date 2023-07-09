from flask import request, Response
import connexion
import json
from database.user_repo import User as UserDB
from database.zke_repo import ZKE as ZKE_DB
from database.storage_key_repo import StorageKeysRepo as StorageKeysDB
from Crypto.hash_func import Bcrypt
import logging
import environment as env
import random
import string
from flask_cors import CORS
import Crypto.jwt_func as jwt_auth
import os
import base64
import uuid
import datetime



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
    
    randomSalt = base64.b64encode(os.urandom(16)).decode('utf-8')
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
        
    storageKeysDb = StorageKeysDB()
    rand_uuid = str(uuid.uuid4())
    storage_key = base64.b64encode(os.urandom(16)).decode('utf-8')
    expiration =  str((datetime.datetime.utcnow() + datetime.timedelta(hours=1)).timestamp())
    try:
        storageKeysDb.create( rand_uuid, storage_key, expiration)
    except Exception as e:
        logging.error("Unknown error while storing user storage keys" + str(e))
        return {"message": "Unknown error while registering user encrypted keys"}, 500
    

    jwt_token = jwt_auth.generate_jwt(user.id)

    try :
        storage_jwt = jwt_auth.generate_jwt(rand_uuid)
    except Exception as e:
        logging.error("Unknown error while generating storage jwt" + str(e))
        return {"message": "Unknown error while generating storage jwt"}, 500
    response = Response(status=200, mimetype="application/json", response=json.dumps({"username": user.username, "id":user.id, "derivedKeySalt":user.derivedKeySalt}))
    response.set_cookie("api-key", jwt_token, httponly=True, secure=True, samesite="Lax")
    response.set_cookie("storage-jwt", storage_jwt, httponly=True, secure=True, samesite="Lax")
    return response
    


#GET /vault
def getVault():
    try:
        user_id = connexion.context.get("user")
        logging.info(user_id)
    except Exception as e:
        logging.info(e)
        return {"message": "Invalid request"}, 400
    

#GET /zke_key
def getZKEKey():
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