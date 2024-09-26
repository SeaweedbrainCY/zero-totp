from app import app
from database.db import db 
import unittest
import controllers
from unittest.mock import patch
from zero_totp_db_model.model import User, TOTP_secret, ZKE_encryption_key
from environment import conf
from CryptoClasses import jwt_func,hash_func
from uuid import uuid4
import json
import jwt
import datetime

class TestUpdateVault(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/update/vault"
        
        self.user_id = 1
        self.nb_totp = 10
        self.password =  hash_func.Bcrypt("HelloWorld!")
        self.jwtCookie = jwt_func.generate_jwt(self.user_id)
        user = User(id=self.user_id,username='user1', mail="user1@test.com", password=self.password.hashpw().decode('utf-8'), derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAA", createdAt="01/01/2001", isBlocked=False)
        self.totp_codes = {}
        zke = ZKE_encryption_key(user_id=self.user_id, ZKE_key="zke_enc")
        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(user)
            db.session.add(zke)
            for i in range(self.nb_totp):
                id = str(uuid4())
                totp = TOTP_secret(uuid=id, user_id=self.user_id, secret_enc = f"enc_{i}")
                self.totp_codes[id] = f"code_{i}-2"
                db.session.add(totp)
            db.session.commit()

            
       

       

        self.payload = {
            "new_passphrase" : "new_passphrase", 
            "old_passphrase":self.password.password, 
            "enc_vault": json.dumps(self.totp_codes), 
            "zke_enc":"zke_enc", 
            "passphrase_salt": "pasphrase_salt", 
            "derived_key_salt":"derived_key_salt"}


    def tearDown(self):
         with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()
    
    def generate_expired_cookie(self):
        payload = {
            "iss": jwt_func.ISSUER,
            "sub": 1,
            "iat": datetime.datetime.utcnow(),
            "nbf": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() - datetime.timedelta(hours=1),
        }
        jwtCookie = jwt.encode(payload, conf.api.jwt_secret, algorithm=jwt_func.ALG)
        return jwtCookie
    
    def test_update_vault(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.put(self.endpoint, json=self.payload)
            self.assertEqual(response.status_code, 201)
            codes = db.session.query(TOTP_secret).filter_by(user_id=self.user_id).all()
            for code in codes:
                self.assertEqual(code.secret_enc, self.totp_codes[code.uuid])


    

    def test_update_vault_no_cookie(self):
        response = self.client.put(self.endpoint)
        self.assertEqual(response.status_code, 401)
    
    def test_update_vault_bad_cookie(self):
        self.client.cookies = {"api-key": "badcookie"}
        response = self.client.put(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_update_vault_expired_jwt(self):
        self.client.cookies = {"api-key": self.generate_expired_cookie()}
        response = self.client.put(self.endpoint)
        self.assertEqual(response.status_code, 403)

    def test_update_vault_bad_args(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        for key in self.payload.keys():
            payload = self.payload.copy()
            payload.pop(key)
            response = self.client.put(self.endpoint, json=payload)
            self.assertEqual(response.status_code, 400)

        for key in self.payload.keys():
            payload = self.payload.copy()
            payload[key] = ""
            response = self.client.put(self.endpoint, json=payload)
            self.assertEqual(response.status_code, 400)
    

    def test_update_vault_wrong_passphrase(self):
        self.payload["old_passphrase"] = "wrong"
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"message": "Invalid passphrase"})


    def test_update_vault_passphrase_too_long(self):
        self.payload["new_passphrase"] = "a"*100
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual({"message": "passphrase too long. It must be <70 char"}, response.json())
    

    def test_update_vault_unknown_totp(self):
        self.totp_codes.pop(-1)
        self.totp_codes[str(uuid4())] = "code"
        self.payload["enc_vault"] = json.dumps(self.totp_codes)
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message": "To avoid the loss of your information, Zero-TOTP is rejecting this request because it has detected that you might lose data. Please contact quickly Zero-TOTP developers to fix issue."}, 400)
"""   
    def test_update_vault_unknown_totp_failed(self):
        self.getSecretByUUID.return_value = None
        self.addSecret.return_value = False
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["totp"], 0)

    def test_update_vault_wrong_totp_user_id(self):
        self.getSecretByUUID.return_value = TOTP_secret(user_id=2)
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["totp"], 0)
    
    def test_update_vault_update_totp_failed(self):
        self.updateSecret.return_value = None 
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["totp"], 0)
    
    def test_update_vault_failed_update_zke(self):
        self.zkeUpdate.return_value = None 
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["zke"], 0)
    
    def test_update_vault_failed_update_user(self):
        self.updateUser.return_value = None 
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["user"], 0)
    
    def test_update_vault_unverified_user(self):
        self.getById.return_value = User(id=1, isVerified=False, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001", isBlocked=False)
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], "Not verified")
    
    def test_update_vault_blocked_user(self):
        self.getById.return_value = User(id=1, isVerified=True, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001", isBlocked=True)
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], "User is blocked")
    
    def test_update_invalid_vault(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        payload = self.payload.copy()
        payload["enc_vault"] = '{"test": "secret"}'
        response = self.client.put(self.endpoint, json=payload)
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.json()["message"], "The vault submitted is invalid. If you submitted this vault through the web interface, please report this issue to the support.")
    

    """
    