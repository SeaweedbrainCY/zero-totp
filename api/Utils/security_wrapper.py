from database.user_repo import User as UserDB
from CryptoClasses.jwt_func import verify_jwt
import connexion

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

def require_admin_token(func):
     def wrapper(*args, **kwargs):
        try:
            user_id = connexion.context.get("user")
            admin_cookie = connexion.request.cookies.get("admin-api-key")
        except:
            return {"error": "Unauthorized"}, 401
        try:
            jwt_token = verify_jwt(admin_cookie)
        except:
            return {"error": "Unauthorized"}, 403
        user = UserDB().getById(user_id)
        if user == None:
            return {"error": "Forbidden"}, 403
        if user.role != "admin":
            return {"error": "Unauthorized"}, 403
        if jwt_token == None:
            return {"error": "Unauthorized"}, 403
        if "admin" not in jwt_token:
            return {"error": "Unauthorized"}, 403
        if jwt_token["admin"] == True:
            return func(*args, **kwargs)
        return {"error": "Unauthorized"}, 403
     return wrapper