from database.user_repo import User as UserDB
from CryptoClasses.jwt_func import verify_jwt
import connexion
from environment import logging
from CryptoClasses.hash_func import Bcrypt
import random
import string

def require_admin_role(func):
    def wrapper(context_, user, token_info,*args, **kwargs):
        try:
            user_id = context_["user"]
        except:
            return {"error": "Unauthorized"}, 401
        user_obj = UserDB().getById(user_id)
        if user_obj == None:
            return {"error": "Forbidden"}, 403
        if user_obj.role == "admin":
            return func(user_id,*args, **kwargs)
        return {"error": "Unauthorized"}, 403
    return wrapper


# By design, the admin role is required and checked before the admin token. 
# The require_admin_role wrapper must not be removed without adding the admin role check in the require_admin_token wrapper.
def require_admin_token(func):
     @require_admin_role
     def wrapper(user_id,*args, **kwargs):
        try:
            admin_cookie = connexion.request.cookies["admin-api-key"]
        except:
            logging.info("Admin token rejected because of missing cookie or user id")
            return {"error": "Unauthorized"}, 403
        try:
            jwt_token = verify_jwt(admin_cookie)
        except Exception as e:
            logging.info("Admin token rejected because of bad admin cookie. " + str(e))
            return {"error": "Unauthorized"}, 403
        user = UserDB().getById(user_id)
        if jwt_token == None:
            logging.info("Admin token rejected because of bad admin cookie")
            return {"error": "Unauthorized"}, 403
        if "admin" not in jwt_token:
            logging.info("Admin token rejected because of admin cookie doesn't have admin field")
            return {"error": "Unauthorized"}, 403
        if user_id != int(jwt_token["sub"]):
            logging.info("Admin token rejected because of admin cookie doesn't have same user id as the main cookie")
            return {"error": "Unauthorized"}, 403
        if jwt_token["admin"] == True:
            logging.info("Admin token accepted for user " + str(user_id))
            return func(*args, **kwargs)
        logging.info("Admin token rejected because of admin cookie admin field is false")
        return {"error": "Unauthorized"}, 403
     return wrapper

def require_userid(func):
    def wrapper(context_, user, token_info, *args, **kwargs):
        try:
            user_id = context_["user"]
            if user_id == None:
                return {"error": "Unauthorized"}, 401
        except:
            return {"error": "Unauthorized"}, 401
        return func(user_id, *args, **kwargs)
    return wrapper


# By design, the user id is required and checked before the user token.
# Require x-hash-passphrase header and check it against the user's hashed passphrase
def require_passphrase_verification(func):
    def wrapper(context_, user, token_info, *args, **kwargs):
        try:
            user_id = context_["user"]
            if user_id == None:
                return {"error": "Unauthorized"}, 401
        except:
            return {"error": "Unauthorized"}, 401
        try:
            passphrase = connexion.request.headers["x-hash-passphrase"]
        except:
            return {"error": "Unauthorized"}, 401
        user_obj = UserDB().getById(user_id)
        bcrypt = Bcrypt(passphrase)

        if user_obj == None:
            logging.info("User " + str(user_id) + " tried to login but does not exist. A fake password is checked to avoid timing attacks")
            fake_password = ''.join(random.choices(string.ascii_letters, k=random.randint(10, 20)))
            bcrypt.checkpw(fake_password)
            return {"message": "Invalid credentials"}, 403
        if bcrypt.checkpw(user.password):
            return func(user_id, *args, **kwargs)
        return {"error": "Unauthorized"}, 403