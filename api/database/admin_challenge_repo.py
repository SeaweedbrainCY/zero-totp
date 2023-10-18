from database.db import db 
from database.model import Admin_challenge as Admin_challenge_model

class Admin_challenge:
   def update_random_challenge(self, user_id, random_challenge, expiration):
        admin_challenge = db.session.query(Admin_challenge_model).filter_by(user_id=user_id).first()
        if admin_challenge == None:
            return None
        admin_challenge.challenge = random_challenge
        admin_challenge.challenge_expiration = expiration
        db.session.commit()
        return admin_challenge