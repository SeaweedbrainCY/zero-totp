import jwt
from environment import conf
from functools import wraps
import uuid
import jwt
import datetime
from flask import jsonify, request
import logging
from connexion.exceptions import Forbidden

ALG = 'HS256'
ISSUER = "https://zero-totp.com/api/v1"

# Verification performed by openAPI
def verify_jwt(jwt_token): 
   try:
        data = jwt.decode(jwt_token,
                           conf.api.jwt_secret, 
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
        jti = str(uuid.uuid4())
        payload = {
            "iss": ISSUER,
            "sub": user_id,
            "jti": jti,
            "iat": datetime.datetime.utcnow(),
            "nbf": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        }
        if admin:
            payload["admin"] = True
            payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        return jwt.encode(payload, conf.api.jwt_secret, algorithm=ALG), jti
    except Exception as e:
        logging.warning("Error while generating JWT : " + str(e))
        raise e

