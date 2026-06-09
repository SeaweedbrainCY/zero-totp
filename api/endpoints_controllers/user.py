from environment import conf, logging
from Utils.security_wrapper import require_active_user
from database.user_repo import User as UserRepo
from database.update_passphrase_repo import UpdatePassphraseRepo
from database.totp_secret_repo import TOTP_secret as TOTP_secretDB
from CryptoClasses.hash_func import Bcrypt
import Utils.utils as utils
from flask import request, redirect, make_response
import threading


# GET /user/derived-key-salt
@require_active_user
def get_derived_key_salt(src_ip, user_obj):
    """
    Returns the derived key salt for the user.
    """
    return {"derived_key_salt": user_obj.derivedKeySalt}, 200
    

#PUT /update/vault 
@require_active_user
def update_vault(src_ip, user_obj, body):
    try:
        newPassphrase: str = body["new_passphrase"].strip()
        old_passphrase:str = body["old_passphrase"].strip()
        enc_vault: list[dict[str, str]]  = body["enc_vault"]
        zke_key: str = body["zke_enc"].strip()
        passphrase_salt: str = body["passphrase_salt"].strip()
        derivedKeySalt:str = body["derived_key_salt"].strip()
    except Exception as e:
        logging.error(e)
        return '{"message": "Invalid request"}', 400

    if not newPassphrase or not old_passphrase or not zke_key or not passphrase_salt or not derivedKeySalt:
        return {"message": "Missing parameters"}, 400
    
    
    totp_secretDB = TOTP_secretDB()

    bcrypt = Bcrypt(old_passphrase)
    if not bcrypt.checkpw(user_obj.password):
        logging.info("User " + str(user_obj.id) + " tried to update his vault but provided passphrase is wrong.")
        return {"message": "Invalid passphrase"}, 403
    bcrypt = Bcrypt(newPassphrase)
    try:
        hashedpw = bcrypt.hashpw()
    except ValueError as e:
        logging.warning(e)
        return {"message": "passphrase too long. It must be <70 char"}, 400
    except Exception as e:
        logging.warning("Uknown error occured while hashing password" + str(e))
        return {"message": "Internal Server Error. Code 56af5a20-c8c8-4b30-89ff-a8ae5b57c865."}, 500

    logging.info(f"User {user_obj.id} is updating their passphrase. Old passphrase is verified. Proceeding with vault update. IP : {utils.get_ip(request)}")
    
    old_vault = TOTP_secretDB().get_all_enc_secret_by_user_id(user_obj.id)
    if len(old_vault) != len(enc_vault):
        logging.warning(f"User {user_obj} tried to update his vault but the number of secrets in the new vault is different from the old one. The update is rejected.")
        return {"message": "To avoid the loss of your information, Zero-TOTP is rejecting this request because it has detected that you might lose data. Please contact quickly Zero-TOTP developers to fix issue."}, 400
    
    uuids_from_old_vault = [secret.uuid for  secret in old_vault]
    uuids_from_new_vault = [item["uuid"] for  item in enc_vault]

    for item in enc_vault:
        if item["uuid"] not in uuids_from_old_vault:
            logging.warning(f"FORBIDDEN. The user {user_obj.id} tried to update but the secret {item['uuid']} was not in his vault. The update is rejected.")
            return {"message": "Forbidden action. Zero-TOTP detected that you were updating object you don't have access to. The request is rejected."}, 403


    for secret in old_vault:
        if secret.uuid not in uuids_from_new_vault:
            logging.warning(f"Error. The user {user_obj.id} tried to update but the secret {secret.uuid} was not sent in his new vault. This means the secret would not have been updated. The update is rejected.")
            return {"message": "Missing parameters. One of the user's secret would not have been updated because missing from the update request. Request aborted."}, 400
        
    

    try:
        UpdatePassphraseRepo().updatePassphrase(user_id=user_obj.id, newPassphrase=hashedpw, newZKEKey=zke_key, newPassphraseSalt=passphrase_salt, newDerivedKeySalt=derivedKeySalt, newVault=enc_vault)
    except Exception as e:
        logging.error(f"An error occured while updating the passphrase of user {user_obj.id}. Error: {e}")
        return {"message": "Internal Server Error. Code 26db0b56-c51e-4515-a4ae-f3e4927f7da2."}, 500
    try:
        ip = utils.get_ip(request)
        thread = threading.Thread(target=utils.send_information_email,args=(ip, user_obj.mail, "Your vault passphrase has been updated"))
        thread.start()
    except Exception as e:
        logging.error("Unknown error while sending information email" + str(e))
    logging.info(f"User {user_obj.id} has successfully updated their vault and passphrase.")
    return {"message": "Vault updated"}, 201