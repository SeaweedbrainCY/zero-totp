import jwt
import environment as env
from functools import wraps
import uuid
import jwt
import datetime
from flask import jsonify, request
import logging
from werkzeug.exceptions import Forbidden


# Verification performed by openAPI
def verify_jwt(jwt_token): 
   try:
        data = jwt.decode(jwt_token,
                           env.jwt_secret, 
                           algorithms=["HS256"], 
                           verify=True, 
                           iss="https://api.zero-totp.fr",
                           options={
                              "verify_iss": True, 
                              "verify_nbf": True, 
                              "verify_exp": True, 
                              "verify_iat":True})
        return data
   except Exception as e:
       logging.warning("Invalid token : " + str(e))
       raise Forbidden("Invalid token")



def generate_jwt(user_id):
    try:
        payload = {
            "iss": "https://api.zero-totp.fr",
            "sub": user_id,
            "iat": datetime.datetime.utcnow(),
            "nbf": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        }
        return jwt.encode(payload, env.jwt_secret, algorithm="HS256")
    except Exception as e:
        logging.warning("Error while generating JWT : " + str(e))
        raise e

