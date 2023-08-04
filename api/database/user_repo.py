from database.db import db 
from database.model import User as UserModel
import logging

class User:

    def getByEmail(self, email):
        return db.session.query(UserModel).filter_by(mail=email).first()
    
    def create(self, username, email, password, randomSalt, isVerified, passphraseSalt):
        user = UserModel(username=username, mail=email, password=password, derivedKeySalt=randomSalt, isVerified = isVerified, passphraseSalt = passphraseSalt)
        db.session.add(user)
        db.session.commit()
        return user
    
    def delete(self, user_id):
        db.session.query(UserModel).filter_by(id=user_id).delete()
        db.session.commit()
        return True
    
    def update_email(self, user_id, email):
        user = db.session.query(UserModel).filter_by(id=user_id).first()
        if user == None:
            return None
        user.mail = email
        db.session.commit()
        return user