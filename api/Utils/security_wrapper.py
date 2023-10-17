from database.user_repo import User as UserDB
import connexion

def admin_restricted(func):
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
        