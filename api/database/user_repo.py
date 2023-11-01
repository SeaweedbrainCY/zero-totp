from database.db import db 
from database.model import User as UserModel
from environment import logging

class User:

    def getByEmail(self, email):
        return db.session.query(UserModel).filter_by(mail=email).first()
    
    def getById(self, user_id):
        return db.session.query(UserModel).filter_by(id=user_id).first()
    
    def create(self, username, email, password, randomSalt, isVerified, passphraseSalt, today):
        user = UserModel(username=username, mail=email, password=password, derivedKeySalt=randomSalt, isVerified = isVerified, passphraseSalt = passphraseSalt, createdAt=today)
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
    
    def update(self, user_id, passphrase, passphrase_salt, derivedKeySalt):
        user = db.session.query(UserModel).filter_by(id=user_id).first()
        if user == None:
            return None
        user.password = passphrase
        user.passphraseSalt = passphrase_salt
        user.derivedKeySalt = derivedKeySalt
        db.session.commit()
        return user

    def update_role(self, user_id, new_role):
        user = db.session.query(UserModel).filter_by(id=user_id).first()
        if user == None:
            return None
        user.role = new_role
        db.session.commit()
        return user
    
    def get_all(self):
        return db.session.query(UserModel).all()
