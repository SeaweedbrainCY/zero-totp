from Utils.security_wrapper import  require_valid_user
from Utils import utils
from Services.vault import encrypted_secrets as encrypted_secrets_services
from environment import logging


# POST /encrypted_secrets 
@require_valid_user
def mass_add_encrypted_secrets(user_id, body):
    encrypted_secrets_list = []
    for enc_secret in body["encrypted_secrets_list"]
        encrypted_secrets_list.append(utils.sanitize_input(enc_secret))
    if len(encrypted_secrets_list) > 100:
        return {"message": "The number of maximum encrypted secrets submitted is over the limit."}, 400
    
    secrets_uuid_list = []
    addition_error = False
    for encrypted_secret in encrypted_secrets_list:
        try:
            secret_uuid = encrypted_secrets_services.add_new_encrypted_secret_to_database(encrypted_secret=encrypted_secret, user_id=user_id)
            secrets_uuid_list.append(secret_uuid)
        except Exception as e:
            logging.warning(f"Throwing error 500 for POST /encrypted_secret of user {user_id}. Error : {e}")
            addition_error = True
    
    if addition_error:
        return {"message": "Unknown error while adding encrypted secret. Some added secrets might have been added.", "uuid_list":secrets_uuid_list}, 500
    
    return {"message": "OK", "uuid_list":secrets_uuid_list}, 201

#POST /encrypted_secret
@require_valid_user
def add_encrypted_secret(user_id, body):
    enc_secret = utils.sanitize_input(body["enc_secret"]).strip()
    secret_uuid = ""
    try:
        secret_uuid = encrypted_secrets_services.add_new_encrypted_secret_to_database(encrypted_secret=enc_secret, user_id=user_id)
    except Exception as e:
        logging.warning(f"Throwing error 500 for POST /encrypted_secret of user {user_id}. Error : {e}")
        return {"message": "Unknown error while adding encrypted secret"}, 500
    
    return {"uuid": secret_uuid}, 201
        
    
