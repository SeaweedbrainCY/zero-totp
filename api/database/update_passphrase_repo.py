# This is a dedicated repo to handle passphrase update management.
# To securely update the passphrase, the passphrase, vault and encrypted zke key need to be update at once. 

from database.db import db 
from zero_totp_db_model.model import TOTP_secret as TOTP_secret_model
from zero_totp_db_model.model import ZKE_encryption_key as ZKEModel
from zero_totp_db_model.model import User as UserModel



class UpdatePassphraseRepo:

    def updatePassphrase(self, user_id:str,  newPassphrase:str, newVault: list[dict[str, str]], newZKEKey: str, newPassphraseSalt:str, newDerivedKeySalt:str)  :
        try:
            with db.session.begin():
                for item in newVault:
                    secret_item = db.session.query(TOTP_secret_model).filter_by(uuid=item["uuid"], user_id=user_id).first()
                    if secret_item is None:
                        raise Exception(f"Secret {item['uuid']} not found for user {user_id}. Transaction aborted.")
                    secret_item.secret_enc = item["enc_secret"]

                zke_key = db.session.query(ZKEModel).filter_by(user_id=user_id).first()
                if zke_key is None:
                    raise Exception(f"ZKE key for user {user_id} not found. Transaction aborted.")

                zke_key.ZKE_key = newZKEKey

                user = db.session.query(UserModel).filter_by(id=user_id).first()
                if user == None:
                    raise Exception(f"{user_id} not found. Transaction aborted.")
                user.password = newPassphrase
                user.passphraseSalt = newPassphraseSalt
                user.derivedKeySalt = newDerivedKeySalt
        
        except Exception:
            db.session.rollback()
            raise



            

            



