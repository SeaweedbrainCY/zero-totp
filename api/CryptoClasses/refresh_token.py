from uuid import uuid4
from hashlib import sha256
from database.refresh_token_repo import RefreshTokenRepo
from environment import logging
import datetime as dt
from CryptoClasses.jwt_func import generate_jwt, verify_jwt
from connexion.exceptions import Forbidden, Unauthorized



def generate_refresh_token(user_id, jti, expiration=-1):
    token = str(uuid4())
    hashed_token = sha256(token.encode()).hexdigest()
    rt_repo = RefreshTokenRepo()
    rt = rt_repo.create_refresh_token(user_id, jti, hashed_token, expiration=expiration)
    return token if rt else None
    
    
def refresh_token_flow(jti, rt, jwt_user_id):
        rt_repo = RefreshTokenRepo()
        if rt.jti == jti and rt.user_id == jwt_user_id:
            if rt.revoke_timestamp == None:
                if float(rt.expiration) > dt.datetime.now(dt.UTC).timestamp():
                    new_jwt = generate_jwt(rt.user_id)
                    new_jti = verify_jwt(new_jwt)["jti"]
                    new_refresh_token = generate_refresh_token(rt.user_id, new_jti, expiration=rt.expiration)
                    rt_repo.revoke(rt.id)
                    return new_jwt, new_refresh_token
                else:
                    logging.warning(f"The user {rt.user_id} tried to refresh a token that has expired: {rt.id}. Refresh flow aborted. Token expired at: {rt.expiration}")
                    raise Forbidden("Access denied")
            else:
                logging.warning(f"The user {rt.user_id} tried to refresh a token that has been revoked: {rt.id}. Refresh flow aborted. Token revoked at: {rt.revoke_timestamp}")
                raise Forbidden("Access denied")
        else:
            logging.warning(f"A refresh token has been asked, but invalid context for refresh token {rt.id}. Expected jti: {rt.jti}, user_id: {rt.user_id}. But git jti: {jti}, user_id: {jwt_user_id}. Refresh flow aborted.")
            rt_repo.revoke(rt.id)
            raise Forbidden("Access denied")


