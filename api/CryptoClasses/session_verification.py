from database.session_token_repo import SessionTokenRepo
from flask import request
from app import app
from connexion.exceptions import Unauthorized, Forbidden
from hashlib import sha256
from environment import logging
from Utils.utils import get_ip
import datetime as dt

def verify_session(token_info):
    if not token_info:
        raise Unauthorized("No session token provided")
    with app.app.app_context():
        remote_ip = get_ip(request)
        session_token = SessionTokenRepo().get_session_token(token_info)
        if not session_token:
            raise Unauthorized("Invalid session token")
        if float(session_token.expiration) < dt.datetime.now(dt.UTC).timestamp():
            raise Unauthorized("API key expired")
        if session_token.revoke_timestamp is not None:
            logging.info(f"Rejected session token {session_token.id} because it was revoked. User {session_token.user_id} from IP {remote_ip}")
            raise Forbidden("Invalid session token")
        return  {"uid" : session_token.user_id}