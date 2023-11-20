from database.user_repo import User as UserDB
from CryptoClasses.jwt_func import verify_jwt
import connexion
from environment import logging

def require_admin_role(func):
    def wrapper(context_, user, token_info,*args, **kwargs):
        try:
            user_id = context_["user"]
        except:
            return {"error": "Unauthorized"}, 401
        user = UserDB().getById(user_id)
        if user == None:
            return {"error": "Forbidden"}, 403
        if user.role == "admin":
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