from database.session_token_repo import SessionTokenRepo
from app import app
from connexion.exceptions import Unauthorized, Forbidden
from hashlib import sha256
from environment import logging
from Utils.utils import get_ip
import datetime as dt


def verify_session(token):
    if not token:
        raise Unauthorized("No session token provided")
    with app.app.app_context(): 
        session_token = SessionTokenRepo().get_session_token(token)
        if not session_token:
            logging.info(f"Rejected session token {token} because it does not exist")
            raise Forbidden("Invalid session token")
        if float(session_token.expiration) < dt.datetime.now(dt.UTC).timestamp():
            logging.info(f"Rejected session token {session_token.id} because it has expired. User {session_token.user_id}")
            raise Forbidden("API key expired")
        if session_token.revoke_timestamp is not None:
            logging.info(f"Rejected session token {session_token.id} because it was revoked. User {session_token.user_id}")
            raise Forbidden("Invalid session token")
        return  {"uid" : session_token.user_id}