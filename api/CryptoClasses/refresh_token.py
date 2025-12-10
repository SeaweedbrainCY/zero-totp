from uuid import uuid4
from hashlib import sha256
from database.refresh_token_repo import RefreshTokenRepo
from environment import logging
import datetime as dt
from connexion.exceptions import Forbidden, Unauthorized
from database.rate_limiting_repo import RateLimitingRepo
from database.session_token_repo import SessionTokenRepo
import Utils.utils as utils
from zero_totp_db_model.model import SessionToken as SessionTokenModel, RefreshToken as RefreshTokenModel



def generate_refresh_token(user_id, session_token_id, session, expiration=-1):
    token = str(uuid4())
    hashed_token = sha256(token.encode()).hexdigest()
    rt_repo = RefreshTokenRepo()
    rt = rt_repo.create_refresh_token(user_id, session_token_id, hashed_token, session=session, expiration=expiration)
    return token if rt else None
    
    
def refresh_token_flow(refresh_token:RefreshTokenModel, session_token:SessionTokenModel, ip:str):
    logging.info(f"Refreshing token for user {session_token.user_id}")
    rate_limiting = RateLimitingRepo()
    session_repo = SessionTokenRepo()
    if refresh_token.session_token_id == session_token.id and refresh_token.user_id == session_token.user_id:
        if refresh_token.revoke_timestamp == None:
            if float(refresh_token.expiration) > dt.datetime.now(dt.UTC).timestamp():
                session = session_token.session
                if session.revoke_timestamp is None: 
                    if float(session.expiration_timestamp) > dt.datetime.now(dt.UTC).timestamp():
                        new_session_id, new_session_token = session_repo.generate_session_token(session_token.user_id, session=session)
                        new_refresh_token = generate_refresh_token(session_token.user_id, new_session_id, session=session)
                        utils.revoke_session_and_refresh_tokens(session_id=session_token.id, refresh_id=refresh_token.id)
                        return new_session_token, new_refresh_token
                    else:
                        logging.info(f"Session {session.id} has expired. Refresh flow aborted.")
                        rate_limiting.add_failed_login(ip, refresh_token.user_id)
                        raise Forbidden("Access denied")
                else:
                    logging.info(f"Session {session.id} is revoked. Refresh flow aborted.")
                    rate_limiting.add_failed_login(ip, refresh_token.user_id)
                    raise Forbidden("Access denied")
            else:
                rate_limiting.add_failed_login(ip, refresh_token.user_id)
                logging.warning(f"The user {refresh_token.user_id} tried to refresh a token that has expired: {refresh_token.id}. Refresh flow aborted. Token expired at: {refresh_token.expiration}")
                raise Forbidden("Access denied")
        else:
            rate_limiting.add_failed_login(ip, refresh_token.user_id)
            logging.warning(f"The user {refresh_token.user_id} tried to refresh a token that has been revoked: {refresh_token.id}. Refresh flow aborted. Token revoked at: {refresh_token.revoke_timestamp}")
            raise Forbidden("Access denied")
    else:
        rate_limiting.add_failed_login(ip, session_token.user_id)
        logging.warning(f"A refresh token has been asked, but invalid context for refresh token {refresh_token.id}. Session : Id : {session_token.id}, User {session_token.user_id}. Refresh : Id : {refresh_token.id}, User: {refresh_token.user_id}, Association session id : {refresh_token.session_token_id}. Refresh flow aborted. Revoking all related tokens and their session.")
        utils.revoke_session(session_id=session_token.session.id)
        utils.revoke_session(session_id=refresh_token.session.id)
        raise Forbidden("Access denied")


