from database.user_repo import User as UserDB
import connexion
from environment import logging, conf
from CryptoClasses.hash_func import Bcrypt
import random
import string
import Utils.utils as utils
from database.rate_limiting_repo import RateLimitingRepo as Rate_Limiting_DB
from flask import request
import functools

# only the user id is required. The request is not rejected even if the user is not verified.
def require_userid(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            user_id = kwargs.get("token_info", {}).get("uid") \
                      or kwargs.get("user")
            if not user_id:
                return {"error": "Unauthorized"}, 401
            user = UserDB().getById(user_id)
            if user is None:
                return {"error": "Unauthorized"}, 401
            if user.isBlocked:
                return {"error": "User is blocked"}, 403
        except Exception:
            return {"error": "Unauthorized"}, 401
        return func(*args, **kwargs)
    return wrapper

# Check that the user is verified, not blocked and inject context info
def require_active_user(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        token_info = kwargs.get("token_info")
        if token_info == None:
            return {"error": "Unauthorized"}, 401
        user_id = token_info.get("uid") or kwargs.get("user")
        if user_id == None:
            return {"error": "Unauthorized"}, 401
        user_obj = UserDB().getById(user_id)
        if user_obj == None:
            return {"error": "Unauthorized"}, 401
        if user_obj.isBlocked:
                return {"error": "User is blocked"}, 403
        if not user_obj.isVerified and conf.features.emails.require_email_validation:
            return {"error": "Not verified"}, 403
        src_ip = utils.get_ip(connexion.request)
        return func(src_ip, user_obj, *args, **kwargs)
    return wrapper

# By design, the user id is required and checked before the user token.
# Require x-hash-passphrase header and check it against the user's hashed passphrase
def require_passphrase_verification(func):
    @functools.wraps(func)
    @require_active_user
    def wrapper(*args, **kwargs):
        try:
            passphrase = connexion.request.headers["x-hash-passphrase"]
        except KeyError:
            return {"error": "Unauthorized"}, 401

        user = UserDB().getById(user_id)
        if user == None:
            return {"error": "Unauthorized"}, 401
        bcrypt = Bcrypt(passphrase)

        if not bcrypt.checkpw(user.password):
            return {"error": "Unauthorized"}, 403
        return func(*args, **kwargs)
    return wrapper


def ip_rate_limit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ip = utils.get_ip(connexion.request)
        if ip and Rate_Limiting_DB().is_login_rate_limited(ip):
            return {"message": "Too many requests",
                    "ban_time": conf.features.rate_limiting.login_ban_time}, 429
        kwargs["_ip"] = ip
        return func(*args, **kwargs)
    return wrapper