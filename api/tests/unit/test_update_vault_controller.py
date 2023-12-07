import unittest
import controllers
from app import app
from unittest.mock import patch
from database.model import User, TOTP_secret, ZKE_encryption_key
import environment as env
from CryptoClasses import jwt_func,hash_func

import jwt
import datetime

class TestUpdateVault(unittest.TestCase):

    def setUp(self):
        if env.db_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.application.test_client()
        self.endpoint = "/update/vault"
        

        self.getById = patch("database.user_repo.User.getById").start()
        self.getById.return_value = User(id=1, isVerified=True, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001", isBlocked=False)

        self.checkpw = patch("CryptoClasses.hash_func.Bcrypt.checkpw").start()
        self.checkpw.return_value = True

        self.hashpw = patch("CryptoClasses.hash_func.Bcrypt.hashpw").start()
        self.hashpw.return_value = "new_passphrase"

        self.getSecretByUUID = patch("database.totp_secret_repo.TOTP_secret.get_enc_secret_by_uuid").start()
        self.getSecretByUUID.return_value = TOTP_secret(uuid="uuid", user_id=1)

        self.updateSecret = patch("database.totp_secret_repo.TOTP_secret.update_secret").start()
        self.updateSecret.return_value = True

        self.addSecret = patch("database.totp_secret_repo.TOTP_secret.add").start()
        self.addSecret.return_value = True

        self.zkeUpdate = patch("database.zke_repo.ZKE.update").start()
        self.zkeUpdate.return_value = True

        self.updateUser = patch("database.user_repo.User.update").start()
        self.updateUser.return_vtest_update_vault_new_passphrase_bad_formatalue = True

       

        self.payload = {"new_passphrase" : "new_passphrase", "old_passphrase":"old_passphrase", "enc_vault":"{\"uuid\": \"secret\"}", "zke_enc":"zke_enc", "passphrase_salt": "pasphrase_salt", "derived_key_salt":"derived_key_salt"}


    def tearDown(self):
        patch.stopall()
    
    def generate_expired_cookie(self):
        payload = {
            "iss": jwt_func.ISSUER,
            "sub": 1,
            "iat": datetime.datetime.utcnow(),
            "nbf": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() - datetime.timedelta(hours=1),
        }
        jwtCookie = jwt.encode(payload, env.jwt_secret, algorithm=jwt_func.ALG)
        return jwtCookie
    
    def test_update_vault(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 201)
        self.updateUser.assert_called_once()
        self.updateSecret.assert_called_once()
        self.zkeUpdate.assert_called_once()
    

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
        self.checkpw.return_value = False
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 403)
    
    def test_update_vault_passphrase_too_long(self):
        self.hashpw.side_effect = ValueError
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["hashing"], 0)
    

    def test_update_vault_passphrase_error(self):
        self.hashpw.side_effect = Exception
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["hashing"], 0)

    def test_update_vault_unknown_totp(self):
        self.getSecretByUUID.return_value = None
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 201)
        self.addSecret.assert_called_once()
    
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



    
        


    
    