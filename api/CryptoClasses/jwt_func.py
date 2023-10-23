import jwt
import environment as env
from functools import wraps
import uuid
import jwt
import datetime
from flask import jsonify, request
import logging
from werkzeug.exceptions import Forbidden

ALG = 'HS256'
ISSUER = "https://api.zero-totp.com"

# Verification performed by openAPI
def verify_jwt(jwt_token): 
   try:
        data = jwt.decode(jwt_token,
                           env.jwt_secret, 
                           algorithms=[ALG], 
                           verify=True, 
                           issuer = ISSUER,
                           options={
                              "verify_iss": True, 
                              "verify_nbf": True, 
                              "verify_exp": True, 
                              "verify_iat":True})
        return data
   except Exception as e:
       logging.warning("Invalid token : " + str(e))
       raise Forbidden("Invalid token")



def generate_jwt(user_id, admin=False):
    try:
        payload = {
            "iss": ISSUER,
            "sub": user_id,
            "iat": datetime.datetime.utcnow(),
            "nbf": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        }
        if admin:
            payload["admin"] = True
            payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        return jwt.encode(payload, env.jwt_secret, algorithm=ALG)
    except Exception as e:
        logging.warning("Error while generating JWT : " + str(e))
        raise e

