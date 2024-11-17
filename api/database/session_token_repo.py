from database.db import db 
from zero_totp_db_model.model import SessionToken
import datetime
from environment import conf
from uuid import uuid4
from hashlib import sha256

class SessionTokenRepo:

    def generate_session_token(self, user_id):
        id = str(uuid4()) 
        token = str(uuid4())
        expiration_timestamp = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=conf.api.session_token_validity)).timestamp()
        session_token = SessionToken(id=id, user_id=user_id, token=token, expiration=expiration_timestamp)
        db.session.add(session_token)
        db.session.commit()
        return id, token
    
    def get_session_token(self, token):
        return SessionToken.query.filter_by(token=token).first()