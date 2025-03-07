from database.db import db 
from zero_totp_db_model.model import Oauth_tokens as Oauth_tokens_model

class Oauth_tokens:
    def get_by_user_id(self, user_id):
        return db.session.query(Oauth_tokens_model).filter_by(user_id=user_id).first()

    def get_by_entry_id(self, id):
        return db.session.query(Oauth_tokens_model).filter_by(id=id).first()
    
    def add(self, user_id, enc_credentials, expires_at, nonce, tag):
        oauth_tokens = Oauth_tokens_model(user_id=user_id, enc_credentials=enc_credentials, expires_at=expires_at, cipher_nonce=nonce, cipher_tag=tag);
        db.session.add(oauth_tokens)
        db.session.commit()
        return oauth_tokens
    
    def update(self, user_id, enc_credentials, expires_at, nonce, tag):
        oauth_tokens = db.session.query(Oauth_tokens_model).filter_by(user_id=user_id).first()
        if oauth_tokens == None:
            return None
        oauth_tokens.enc_credentials = enc_credentials
        oauth_tokens.expires_at = expires_at
        oauth_tokens.cipher_nonce = nonce
        oauth_tokens.cipher_tag = tag
        db.session.commit()
        return oauth_tokens

    def delete(self, user_id):
        if db.session.query(Oauth_tokens_model).filter_by(user_id=user_id).first() != None:
            db.session.query(Oauth_tokens_model).filter_by(user_id=user_id).delete()
        db.session.commit()
        return True