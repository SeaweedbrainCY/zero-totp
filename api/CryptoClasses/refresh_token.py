from uuid import uuid4
from hashlib import sha256
from database.refresh_token_repo import RefreshTokenRepo
from environment import logging
import datetime as dt
from CryptoClasses.jwt_func import generate_jwt, get_jti_from_jwt


def generate_refresh_token(user_id, jti, expiration=-1):
    token = str(uuid4())
    hashed_token = sha256(token.encode()).hexdigest()
    rt_repo = RefreshTokenRepo()
    rt = rt_repo.create_refresh_token(user_id, jti, hashed_token, expiration=expiration)
    return token if rt else None
    
    
def refresh_token_flow(jti, user_id, token):
    rt_repo = RefreshTokenRepo()
    hashed_token = sha256(token.encode()).hexdigest()
    rt = rt_repo.get_refresh_token_by_hash(hashed_token)
    if rt :
        if rt.jti == jti and rt.user_id == user_id:
            if rt.revoke_timestamp == None:
                if rt.expiration > dt.datetime.now(dt.UTC).timestamp():
                    new_jwt = generate_jwt(user_id)
                    new_jti = get_jti_from_jwt(new_jwt)
                    new_refresh_token = generate_refresh_token(user_id, new_jti, expiration=rt.expiration)
                    rt_repo.revoke(rt.id)
                    return new_jwt, new_refresh_token
                else:
                    logging.warning(f"The user {user_id} tried to refresh a token that has expired: {rt.id}. Refresh flow aborted. Token expired at: {rt.expiration}")
                    raise RefreshTokeException(2)
            else:
                logging.warning(f"The user {user_id} tried to refresh a token that has been revoked: {rt.id}. Refresh flow aborted. Token revoked at: {rt.revoke_timestamp}")
                raise RefreshTokeException(4)
        else:
            logging.warning(f"A refresh token has been asked, but invalid context: {rt.id}. Expected jti: {rt.jti}, user_id: {rt.user_id}. But git jti: {jti}, user_id: {user_id}. Refresh flow aborted.")
            rt_repo.revoke(rt.id)
            raise RefreshTokeException(3)
    else:
        logging.warning(f"A refresh token has been asked, but token not found: {hashed_token}")
        raise RefreshTokeException(1)



class RefreshTokeException(Exception):
    # Error codes:
    # 1: Token not found
    # 2: Token expired
    # 3: Invalid context for token
    error_codes = {
        1: "Token not found",
        2: "Token expired",
        3: "Invalid context for token",
        4: "Token revoked",
        5: "Unknown error"

    }
    def __init__(self, error_code):
        self.error_code = error_code
        self.message = self.error_codes[error_code] if error_code in self.error_codes else self.error_codes[5]