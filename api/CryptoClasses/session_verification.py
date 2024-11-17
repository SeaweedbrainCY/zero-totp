from database.session_token_repo import SessionTokenRepo
from flask import request
from app import app
from connexion.exceptions import OAuthProblem
from hashlib import sha256
from environment import logging
from Utils.utils import get_ip
import datetime as dt

def verify_session(token_info):
    remote_ip = get_ip(request)
    if not token_info:
        raise OAuthProblem("No session token provided")
    with app.app.app_context():
        session_token = SessionTokenRepo().get_session_token(token_info["session-token"])
    if not session_token:
        raise OAuthProblem("Invalid session token")
    if session_token.expiration < dt.datetime.now(dt.UTC).timestamp():
        logging.info(f"Rejected session token {session_token.id} because of expiration. User {session_token.user_id} from IP {remote_ip}")
        raise OAuthProblem("Invalid session token")
    if session_token.revoke_timestamp is not None:
        logging.info(f"Rejected session token {session_token.id} because it was revoked. User {session_token.user_id} from IP {remote_ip}")
        raise OAuthProblem("Invalid session token")
    return  {"uid" : session_token.user_id}