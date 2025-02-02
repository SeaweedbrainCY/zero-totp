from database.db import db 
from zero_totp_db_model.model import User as UserModel
from environment import logging
import datetime as dt

class User:

    def getByEmail(self, email):
        return db.session.query(UserModel).filter_by(mail=email).first()
    
    def getByUsername(self, username):
        return db.session.query(UserModel).filter_by(username=username).first()
    
    def getById(self, user_id):
        return db.session.query(UserModel).filter_by(id=user_id).first()
    
    def create(self, username, email, password, randomSalt, passphraseSalt, today, role="user", isVerified=False, isBlocked=False) -> UserModel:
        user = UserModel(username=username, mail=email, password=password, derivedKeySalt=randomSalt, isVerified = isVerified, passphraseSalt = passphraseSalt, createdAt=today, role=role, isBlocked=isBlocked)
        db.session.add(user)
        db.session.commit()
        return user
    
    def delete(self, user_id):
        db.session.query(UserModel).filter_by(id=user_id).delete()
        db.session.commit()
        return True
    
    def update_email(self, user_id, email, isVerified=False) -> UserModel | None:
        user = db.session.query(UserModel).filter_by(id=user_id).first()
        if user == None:
            return None
        user.mail = email
        user.isVerified = isVerified
        db.session.commit()
        return user

    def update_username(self, user_id, username):
        user = db.session.query(UserModel).filter_by(id=user_id).first()
        if user == None:
            return None
        user.username = username
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
    
    def update_email_verification(self, user_id, isVerified):
        user = db.session.query(UserModel).filter_by(id=user_id).first()
        if user == None:
            return None
        user.isVerified = isVerified
        db.session.commit()
        return user
    
    def update_block_status(self, user_id, block_status):
        user = db.session.query(UserModel).filter_by(id=user_id).first()
        if user == None:
            return None
        user.isBlocked = block_status
        db.session.commit()
        return user
    
    def update_last_login_date(self, user_id):
        user = db.session.query(UserModel).filter_by(id=user_id).first()
        if user == None:
            return None
        user.last_login_date = dt.datetime.now(dt.UTC).timestamp()
        db.session.commit()
        return user
