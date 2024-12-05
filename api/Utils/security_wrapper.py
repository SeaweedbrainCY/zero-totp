from database.user_repo import User as UserDB
import connexion
from environment import logging, conf
from CryptoClasses.hash_func import Bcrypt
import random
import string
import Utils.utils as utils
from database.rate_limiting_repo import RateLimitingRepo as Rate_Limiting_DB
from flask import request



# only the user id is required. The request is not rejected even if the user is not verified.
def require_userid(func):
    def wrapper(context_, user, token_info, *args, **kwargs):
        try:
            user_id = context_["user"]
            if user_id == None:
                return {"error": "Unauthorized"}, 401
            user = UserDB().getById(user_id)
            if user == None :
                return {"error": "Unauthorized"}, 401
            if user.isBlocked :
                return {"error": "User is blocked"}, 403
        except:
            return {"error": "Unauthorized"}, 401
        return func(user_id, *args, **kwargs)
    return wrapper

# Check that the user is verified
def require_valid_user(func):
    @require_userid
    def wrapper(user_id, *args, **kwargs):
        user = UserDB().getById(user_id)
        if user == None:
            return {"error": "Unauthorized"}, 401
        if not user.isVerified and conf.features.emails.require_email_validation:
            logging.info(f"User {user_id} is not verified. Request rejected")
            return {"error": "Not verified"}, 403
        return func(user_id, *args, **kwargs)
    return wrapper

# By design, the user id is required and checked before the user token.
# Require x-hash-passphrase header and check it against the user's hashed passphrase
def require_passphrase_verification(func):
    @require_valid_user
    def wrapper(user_id, *args, **kwargs):
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
        if bcrypt.checkpw(user_obj.password):
            return func(user_id, *args, **kwargs)
        logging.info(f"User {user_id} tried to login with wrong password. require_passphrase_verification wrapper rejected the request")
        return {"error": "Unauthorized"}, 403
    return wrapper

def ip_rate_limit(func):
    def wrapper(*args, **kwargs):
        logging.debug("Rate limiting check")
        ip = utils.get_ip(request)
        rate_limiting_db = Rate_Limiting_DB()
        if ip:
            if rate_limiting_db.is_login_rate_limited(ip):
                logging.info(f"IP {ip} is rate limited")
                return {"message": "Too many requests", 'ban_time':conf.features.rate_limiting.login_ban_time}, 429
        else:
            logging.error("The remote IP used to login is private. The headers are not set correctly")
        return func(ip, *args, **kwargs)
    return wrapper