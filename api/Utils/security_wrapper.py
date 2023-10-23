from database.user_repo import User as UserDB
from CryptoClasses.jwt_func import verify_jwt
import connexion
import logging

def require_admin_role(func):
    def wrapper(*args, **kwargs):
        try:
            user_id = connexion.context.get("user")
        except:
            return {"error": "Unauthorized"}, 401
        user = UserDB().getById(user_id)
        if user == None:
            return {"error": "Forbidden"}, 403
        if user.role == "admin":
            return func(*args, **kwargs)
        return {"error": "Unauthorized"}, 403
    return wrapper


# By design, the admin role is required and checked before the admin token. 
# The require_admin_role wrapper must not be removed without adding the admin role check in the require_admin_token wrapper.
def require_admin_token(func):
     @require_admin_role
     def wrapper(*args, **kwargs):
        try:
            user_id = connexion.context.get("user")
            admin_cookie = connexion.request.cookies.get("admin-api-key")
        except:
            logging.info("Admin token rejected because of missing cookie or user id")
            return {"error": "Unauthorized"}, 401
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