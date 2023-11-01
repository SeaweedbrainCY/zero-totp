import bcrypt
from environment import logging

class Bcrypt():
    password:str
    salt:str

    def __init__(self, password:str):
        self.password = password
        self.salt = bcrypt.gensalt()
    
    def hashpw(self):
        if len(self.password) > 72:
            raise ValueError("Password is too long")
        return bcrypt.hashpw(self.password.encode("utf-8"), self.salt)
    
    def checkpw(self, hashedpw):
        try :
             isOk = bcrypt.checkpw(self.password.encode("utf-8"), hashedpw.encode("utf-8"))
             return isOk
        except Exception as e:
            logging.info("Rejected password : " + str(e))
            return False
