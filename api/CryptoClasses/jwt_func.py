import jwt
from environment import conf
from functools import wraps
from uuid import uuid4
import jwt
import datetime
from flask import jsonify, request
import logging
from connexion.exceptions import Forbidden, Unauthorized
from database.refresh_token_repo import RefreshTokenRepo
ALG = 'HS256'
ISSUER = conf.environment.frontend_URI + "/api/v1"

# Verification performed by openAPI
def verify_jwt(jwt_token, verify_exp=True, verify_revoked=True): 
   try:
        data = jwt.decode(jwt_token,
                           conf.api.jwt_secret, 
                           algorithms=[ALG], 
                           verify=True, 
                           issuer = ISSUER,
                           options={
                              "verify_iss": True, 
                              "verify_nbf": True, 
                              "verify_exp": verify_exp, 
                              "verify_iat":True})
        if verify_revoked:
            associated_refresh_token = RefreshTokenRepo().get_refresh_token_by_jti(data["jti"])
            if associated_refresh_token.revoke_timestamp is not None:
                raise Forbidden("Token revoked")
        return data
   except jwt.ExpiredSignatureError as e:
       raise Unauthorized("API key expired")
   except Exception as e:
       logging.warning("Token verification failed. Invalid token : " + str(e))
       raise Forbidden("Invalid token")


def generate_jwt(user_id, admin=False):
    try:
        payload = {
            "iss": ISSUER,
            "sub": user_id,
            "iat": datetime.datetime.now(datetime.UTC),
            "nbf": datetime.datetime.now(datetime.UTC),
            "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=conf.api.access_token_validity),
            "jti": str(uuid4())
        }
        if admin:
            payload["admin"] = True
            payload["exp"] = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=10)
        return jwt.encode(payload, conf.api.jwt_secret, algorithm=ALG)
    except Exception as e:
        logging.warning("Error while generating JWT : " + str(e))
        raise e

