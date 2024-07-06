from db_models.db import db 
from db_models.model import ZKE_encryption_key as ZKEModel

class ZKE:
   
    def create(self, user_id, encrypted_key):
        zke_keys = ZKEModel(user_id=user_id, ZKE_key=encrypted_key)
        db.session.add(zke_keys)
        db.session.commit()
        return zke_keys
    
    def getByUserId(self, user_id):
        return db.session.query(ZKEModel).filter_by(user_id=user_id).first()
    
    def update(self, user_id, encrypted_key):
        zke_key = self.getByUserId(user_id)
        zke_key.ZKE_key = encrypted_key
        db.session.commit()
        return zke_key
    
    def delete(self, user_id):
        db.session.query(ZKEModel).filter_by(user_id=user_id).delete()
        db.session.commit()
        return True
