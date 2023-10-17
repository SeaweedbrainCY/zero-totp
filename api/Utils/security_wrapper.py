from database.user_repo import User as UserDB
import connexion
from werkzeug.exceptions import Unauthorized, BadRequest


def admin_restricted(func):
    def wrapper(*args, **kwargs):
        try:
            user_id = connexion.context.get("user")
        except:
            raise BadRequest()
        user = UserDB().getById(user_id)
        if user == None:
            return Unauthorized()
        if user.role == "admin":
            return func(*args, **kwargs)
        return Unauthorized()
    return wrapper
        