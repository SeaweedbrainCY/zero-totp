from database.db import db 
from zero_totp_db_model.model import Admin as Admin_model

class Admin:
   def get_by_user_id(self, user_id):
        return db.session.query(Admin_model).filter_by(user_id=user_id).first()