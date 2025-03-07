from database.db import db 
from zero_totp_db_model.model import TOTP_secret as TOTP_secret_model

class TOTP_secret:
    def get_all_enc_secret_by_user_id(self, user_id):
        return db.session.query(TOTP_secret_model).filter_by(user_id=user_id).all()

    def get_enc_secret_of_user_by_uuid(self, user_id, uuid):
        return db.session.query(TOTP_secret_model).filter_by(user_id=user_id, uuid=uuid).first()
    
    def get_enc_secret_by_uuid(self, uuid):
        return db.session.query(TOTP_secret_model).filter_by(uuid=uuid).first()
    
    def add(self, user_id, enc_secret, uuid):
        enc_secret = TOTP_secret_model(user_id=user_id, secret_enc=enc_secret, uuid=uuid)
        db.session.add(enc_secret)
        db.session.commit()
        return enc_secret
    
    def update_secret(self, uuid, enc_secret, user_id):
        enc_totp_secret = db.session.query(TOTP_secret_model).filter_by(uuid=uuid,user_id=user_id ).first()
        if enc_totp_secret == None:
            return None
        enc_totp_secret.secret_enc = enc_secret
        db.session.commit()
        return enc_totp_secret

    def delete(self, user_id, uuid):
        enc_totp_secret = db.session.query(TOTP_secret_model).filter_by(uuid=uuid, user_id=user_id).first()
        if enc_totp_secret == None:
            return None
        db.session.delete(enc_totp_secret)
        db.session.commit()
        return enc_totp_secret
    
    def delete_all(self, user_id):
        db.session.query(TOTP_secret_model).filter_by(user_id=user_id).delete()
        db.session.commit()