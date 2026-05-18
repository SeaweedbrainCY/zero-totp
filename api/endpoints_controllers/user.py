from environment import conf, logging
from Utils.security_wrapper import require_valid_user
from database.user_repo import User as UserRepo
import json


# GET /user/derived-key-salt
@require_valid_user
def get_derived_key_salt(user_id):
    """
    Returns the derived key salt for the user.
    """
    try:
        user = UserRepo().getById(user_id)
        if user is None:
            logging.error(f"User with ID {user_id} not found.")
            return {"error": "User not found"}, 500
        
        return {"derived_key_salt": user.derivedKeySalt}, 200
    except Exception as e:
        logging.error(f"Error retrieving derived key salt for user {user_id}: {str(e)}")
        return {"error": "Internal server error"}, 500


#PUT /update/vault 
@require_valid_user
def update_vault(user_id, body):
    returnJson = {"message": "Internal server error", "hashing":-1, "totp":-1, "user":-1, "zke":-1}
    try:
        newPassphrase = body["new_passphrase"].strip()
        old_passphrase = body["old_passphrase"].strip()
        enc_vault = body["enc_vault"].strip()
        enc_vault = json.loads(enc_vault)
        zke_key = body["zke_enc"].strip()
        passphrase_salt = body["passphrase_salt"].strip()
        derivedKeySalt = body["derived_key_salt"].strip()
    except Exception as e:
        logging.error(e)
        return '{"message": "Invalid request"}', 400

    if not newPassphrase or not old_passphrase or not zke_key or not passphrase_salt or not derivedKeySalt:
        return {"message": "Missing parameters"}, 400
    
    
    
    is_vault_valid, vault_validation_msg = utils.unsafe_json_vault_validation(enc_vault)
    if not is_vault_valid:
        return {"message": vault_validation_msg}, 400
    userDb = UserDB()
    zke_db = ZKE_DB()
    totp_secretDB = TOTP_secretDB()

    user = userDb.getById(user_id)
    bcrypt = Bcrypt(old_passphrase)
    if not bcrypt.checkpw(user.password):
        logging.info("User " + str(user_id) + " tried to update his vault but provided passphrase is wrong.")
        return {"message": "Invalid passphrase"}, 403
    bcrypt = Bcrypt(newPassphrase)
    try :
        hashedpw = bcrypt.hashpw()
    except ValueError as e:
        logging.warning(e)
        return {"message": "passphrase too long. It must be <70 char"}, 400
    except Exception as e:
        logging.warning("Uknown error occured while hashing password" + str(e))
        returnJson["hashing"]=0
        return returnJson, 500

    logging.info(f"User {user_id} is updating their passphrase. Old passphrase is verified. Proceeding with vault update. IP : {utils.get_ip(request)}")
    
    old_vault = TOTP_secretDB().get_all_enc_secret_by_user_id(user_id)
    if len(old_vault) != len(enc_vault):
        logging.warning(f"User {user_id} tried to update his vault but the number of secrets in the new vault is different from the old one. The update is rejected.")
        return {"message": "To avoid the loss of your information, Zero-TOTP is rejecting this request because it has detected that you might lose data. Please contact quickly Zero-TOTP developers to fix issue."}, 400
    for secret in old_vault:
        if secret.uuid not in enc_vault:
            logging.warning(f"FORBIDDEN. The user {user_id} tried to update but the secret {secret.uuid} is missing in the new vault. The update is rejected.")
            return {"message": "Forbidden action. Zero-TOTP detected that you were updating object you don't have access to. The request is rejected."}, 403
    

    returnJson["hashing"]=1
    errors = 0
    for secret in enc_vault.keys():
        totp = totp_secretDB.get_enc_secret_of_user_by_uuid(user_id, secret)
        if not totp:
            totp = totp_secretDB.add(user_id=user_id, enc_secret=enc_vault[secret], uuid=secret)
            if not totp:
                logging.warning("Unknown error while adding encrypted secret for user " + str(user_id))
                errors = 1
        else:
            if totp.user_id != user_id:
                logging.warning("User " + str(user_id) + " tried to update secret " + str(secret) + " which is not his")
                errors = 1
            else :
                totp = totp_secretDB.update_secret(uuid=secret, enc_secret=enc_vault[secret], user_id=user_id)
                if totp == None:
                    logging.warning("User " + str(user_id) + " tried to update secret " + str(secret) + " but an error occurred server side while storing your  encrypted secret")
                    errors = 1
    zke = zke_db.update(user_id, zke_key)
    userUpdated = userDb.update(user_id=user_id, passphrase=hashedpw, passphrase_salt=passphrase_salt, derivedKeySalt=derivedKeySalt)
    returnJson["totp"]=1 if errors == 0 else 0
    returnJson["user"]=1 if userUpdated else 0
    returnJson["zke"]=1 if zke else 0
    if errors == 0 and userUpdated and zke:
        try:
            ip = utils.get_ip(request)
            thread = threading.Thread(target=utils.send_information_email,args=(ip, user.mail, "Your vault passphrase has been updated"))
            thread.start()
        except Exception as e:
            logging.error("Unknown error while sending information email" + str(e))
        logging.info(f"User {user_id} has successfully updated their vault and passphrase.")
        return {"message": "Vault updated"}, 201
    else:
        logging.warning("An error occured while updating passphrase of user " + str(user_id))
        return returnJson, 500
