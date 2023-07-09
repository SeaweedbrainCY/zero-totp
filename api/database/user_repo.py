from database.db import db 
from database.model import User as UserModel

class User:

    def getByEmail(self, email):
        return db.session.query(UserModel).filter_by(mail=email).first()
    
    def create(self, username, email, password, randomSalt):
        user = UserModel(username=username, mail=email, password=password, derivedKeySalt=randomSalt)
        db.session.add(user)
        db.session.commit()
        return user
    
    def delete(self, user_id):
        db.session.query(UserModel).filter_by(id=user_id).delete()
        db.session.commit()
        return True
