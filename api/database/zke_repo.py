from database.db import db 
from database.model import ZKE_encryption_key as ZKEModel

class ZKE:
   
    def create(self, user_id, encrypted_key):
        zke_keys = ZKEModel(user_id=user_id, ZKE_key=encrypted_key)
        db.session.add(zke_keys)
        db.session.commit()
        return zke_keys
