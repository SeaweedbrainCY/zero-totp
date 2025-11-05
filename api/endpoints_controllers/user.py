from environment import conf, logging
from Utils.security_wrapper import require_valid_user
from database.user_repo import User as UserRepo
from database.zke_repo import ZKE as ZKERepo


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


# PUT /vault/passphrase
@require_valid_user
def update_passphrase(user_id, body):
    try:
        new_passphrase_hash = body["new_passphrase_hash"].strip()
        old_passphrase_hash = body["old_passphrase_hash"].strip()
        zke_key = body["zke_enc"].strip()
        passphrase_salt = body["passphrase_salt"].strip()
        derivedKeySalt = body["derived_key_salt"].strip()
    except Exception as e:
        logging.error(e)
        return '{"message": "Invalid request"}', 400
    

    user = UserRepo().getById(user_id)
    if not Bcrypt(old_passphrase_hash).checkpw(user.password):
        logging.info(f"User {user_id} tries to update their passphrase but provides an incorrect old passphrase.")
        return {"message": "The old passphrase is incorrect", "id":"7bad2ddf-75d8-4848-bb16-e15249b98971"}, 403
    
    
    try:
        new_passphrase_bcrypt_hash = Bcrypt(new_passphrase_hash)
    except ValueError as e:
        logging.warning(f"An error occured while hashing password for user {user_id}: {str(e)}")
        return {"message": "passphrase too long. It must be <70 char"}, 400
    except Exception as e:
        logging.warning("Uknown error occured while hashing password" + str(e))
        returnJson["hashing"]=0
        return returnJson, 500
    
    logging.info(f"User {user_id} is updating their passphrase. Old passphrase is verified. Proceeding with ZKE key update. IP : {utils.get_ip(request)}")

    zke_repo = ZKERepo()
    old_zke_key = zke_repo.getByUserId(user_id)
    if old_zke_key is None:
        logging.error(f"ZKE key for user {user_id} not found during passphrase update.")
        return {"message": "Internal server error", "modified":False}, 500
    update_zke_key_status = zke_repo.update(user_id=user_id, encrypted_key=zke_key)
    if not update_zke_key_status:
        logging.error(f"Failed to update ZKE key for user {user_id} during passphrase update.")
        return {"message": "Internal server error", "modified":False}, 500

    update_passphrase_status = UserRepo().update_passphrase(user_id=user_id, passphrase=new_passphrase_bcrypt_hash, passphrase_salt=passphrase_salt, derivedKeySalt=derivedKeySalt)

    if not update_passphrase_status:
        zke_rollback_status = zke_repo.update(user_id=user_id, encrypted_key=old_zke_key.ZKE_key)
        if not zke_rollback_status:
            logging.critical(f"CRITICAL: Failed to rollback ZKE key for user {user_id} after passphrase update failure.")
            return {"message": "Internal server error", "modified":True}, 500
        logging.error(f"Failed to update passphrase for user {user_id}. ZKE key rolled back.")
        return {"message": "Internal server error", "modified":False}, 500
        
    
    try:
        ip = utils.get_ip(request)
        thread = threading.Thread(target=utils.send_information_email,args=(ip, user.mail, "Your vault passphrase has been updated"))
        thread.start()
    except Exception as e:
        logging.error("Unknown error while sending information email" + str(e))
    
    logging.info(f"User {user_id} successfully updated their passphrase and ZKE key.")
    return {"message": "OK"}, 201
    

