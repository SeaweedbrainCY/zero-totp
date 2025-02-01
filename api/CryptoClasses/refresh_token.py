from uuid import uuid4
from hashlib import sha256
from database.refresh_token_repo import RefreshTokenRepo
from environment import logging
import datetime as dt
from connexion.exceptions import Forbidden, Unauthorized
from database.rate_limiting_repo import RateLimitingRepo
from database.session_token_repo import SessionTokenRepo
import Utils.utils as utils



def generate_refresh_token(user_id, session_token_id, expiration=-1):
    token = str(uuid4())
    hashed_token = sha256(token.encode()).hexdigest()
    rt_repo = RefreshTokenRepo()
    rt = rt_repo.create_refresh_token(user_id, session_token_id, hashed_token, expiration=expiration)
    return token if rt else None
    
    
def refresh_token_flow(refresh, session, ip):
        logging.info(f"Refreshing token for user {session.user_id}")
        rate_limiting = RateLimitingRepo()
        session_repo = SessionTokenRepo()
        if refresh.session_token_id == session.id and refresh.user_id == session.user_id:
            if refresh.revoke_timestamp == None:
                if float(refresh.expiration) > dt.datetime.now(dt.UTC).timestamp():
                    new_session_id, new_session_token = session_repo.generate_session_token(session.user_id)
                    new_refresh_token = generate_refresh_token(session.user_id, new_session_id, expiration=refresh.expiration)
                    utils.revoke_session(session_id=session.id, refresh_id=refresh.id)
                    return new_session_token, new_refresh_token
                else:
                    rate_limiting.add_failed_login(ip, refresh.user_id)
                    logging.warning(f"The user {refresh.user_id} tried to refresh a token that has expired: {refresh.id}. Refresh flow aborted. Token expired at: {refresh.expiration}")
                    raise Forbidden("Access denied")
            else:
                rate_limiting.add_failed_login(ip, refresh.user_id)
                logging.warning(f"The user {refresh.user_id} tried to refresh a token that has been revoked: {refresh.id}. Refresh flow aborted. Token revoked at: {refresh.revoke_timestamp}")
                raise Forbidden("Access denied")
        else:
            rate_limiting.add_failed_login(ip, session.user_id)
            logging.warning(f"A refresh token has been asked, but invalid context for refresh token {refresh.id}. Session : Id : {session.id}, User {session.user_id}. Refresh : Id : {refresh.id}, User: {refresh.user_id}, Association session id : {refresh.session_token_id}. Refresh flow aborted.")
            utils.revoke_session(session_id=session.id, refresh_id=refresh.id)
            raise Forbidden("Access denied")


