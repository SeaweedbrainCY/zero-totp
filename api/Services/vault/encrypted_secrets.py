import uuid
from database.totp_secret_repo import TOTP_secret as TOTP_secret_database
from environment import logging
from Services.vault import exceptions

# Manage encrypted secrets logic between controllers and database


def add_new_encrypted_secret_to_database(encrypted_secret:str, user_id:str) -> str:
    secret_uuid = str(uuid.uuid4())
    totp_secret_database =  TOTP_secret_database()

    if totp_secret_database.add(user_id, encrypted_secret, secret_uuid):
        return secret_uuid
    else: 
        logging.warning("Unknown error while adding encrypted secret for user " + str(user_id))
        raise exceptions.UnknownError(f"Unknown error while storing secret id.")
        