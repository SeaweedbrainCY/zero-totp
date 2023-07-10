from database.db import db 
from database.model import Storage_Keys as StorageKeysModel

class StorageKeysRepo:
   
    def create(self, uuid, storage_key, expiration):
        storage_key = StorageKeysModel(uuid=uuid, storage_key=storage_key, expiration=expiration)
        db.session.add(storage_key)
        db.session.commit()
        return storage_key
    
    def getByUUID(self, uuid):
        return db.session.query(StorageKeysModel).filter_by(uuid=uuid).first()
