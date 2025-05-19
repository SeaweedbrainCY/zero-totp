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
    
    def get_session_token_by_id(self, id):
        return SessionToken.query.filter_by(id=id).first()

    def revoke(self, id):
        session_token = SessionToken.query.filter_by(id=id).first()
        session_token.revoke_timestamp = datetime.datetime.now(datetime.UTC).timestamp()
        db.session.commit()
        return session_token
    
    def delete_by_user_id(self, user_id):
        session_tokens = SessionToken.query.filter_by(user_id=user_id).all()
        for session_token in session_tokens:
            db.session.delete(session_token)
        db.session.commit()
        return session_tokens