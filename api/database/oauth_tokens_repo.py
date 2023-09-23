from database.db import db 
from database.model import Oauth_tokens as Oauth_tokens_model

class Oauth_tokens:
    def get_by_user_id(self, user_id):
        return db.session.query(Oauth_tokens_model).filter_by(user_id=user_id).first()
    
    def add(self, user_id, enc_credentials, expires_at):
        oauth_tokens = Oauth_tokens_model(user_id=user_id, enc_credentials=enc_credentials, expires_at=expires_at);
        db.session.add(oauth_tokens)
        db.session.commit()
        return oauth_tokens
    
    def update(self, user_id, enc_credentials, expires_at):
        oauth_tokens = db.session.query(Oauth_tokens_model).filter_by(user_id=user_id).first()
        if oauth_tokens == None:
            return None
        oauth_tokens.enc_credentails = enc_credentials
        oauth_tokens.expires_at = expires_at
        db.session.commit()
        return oauth_tokens