from environment import conf, logging
from Utils.security_wrapper import require_valid_user
from database.user_repo import User as UserRepo


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
