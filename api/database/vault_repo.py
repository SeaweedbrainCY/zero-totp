from database.db import db 
from database.model import Vaults as VaultsModel

class Vault:
    def getVaultByUserId(self, user_id):
        return db.session.query(VaultsModel).filter_by(user_id=user_id).first()
    
    def create(self, user_id, enc_vault):
        vault = VaultsModel(user_id=user_id, enc_vault=enc_vault);
        db.session.add(vault)
        db.session.commit()
        return vault
    
    def updateVault(self, user_id, enc_vault):
        vault = db.session.query(VaultsModel).filter_by(user_id=user_id).first()
        vault.enc_vault = enc_vault
        db.session.commit()
        return vault