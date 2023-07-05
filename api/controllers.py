from flask import request
import json
from database.dbFunctions import User as UserDB
from Crypto.hash_func import Bcrypt
import logging
import environment as env

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
    except :
        logging.warning("Uknown error occured while hashing password")
        return {"message": "Unknown error while hashing your password"}, 500
    
    user = userDB.create(data["username"], data["email"], hashedpw)
    if user :
        return {"message": "User created"}, 201
    else :
        return {"message": "Unknown error while creating user"}, 500

