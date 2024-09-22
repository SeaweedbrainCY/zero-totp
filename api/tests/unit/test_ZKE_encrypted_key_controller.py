from app import app
import unittest
import controllers
from unittest.mock import patch
from zero_totp_db_model.model import ZKE_encryption_key, User
from environment import conf
from CryptoClasses import jwt_func
import jwt
import datetime


class TestZKEEncryptedKey(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.application.test_client()
        self.endpoint = "/api/v1/zke_encrypted_key"
        

        self.get_zke_enc = patch("database.zke_repo.ZKE.getByUserId").start()
        self.get_zke_enc.return_value = ZKE_encryption_key(id=1, user_id=1, ZKE_key="encrypted_key")

        self.getUserByID = patch("database.user_repo.User.getById").start()
        self.getUserByID.return_value = User(id=1, isBlocked=False, isVerified=True, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")


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
        jwtCookie = jwt.encode(payload, conf.api.jwt_secret, algorithm=jwt_func.ALG)
        return jwtCookie
    
    def test_get_ZKE_encrypted_key(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertIn("zke_encrypted_key", response.json())
        self.get_zke_enc.assert_called_once()
    
    def test_get_ZKE_encrypted_key_no_cookie(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 401)
    
    def test_get_ZKE_encrypted_key_bad_cookie(self):
        self.client.cookies = {"api-key":"badcookie"}
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_get_ZKE_encrypted_key_expired_jwt(self):
        self.client.cookies = {"api-key":self.generate_expired_cookie()}
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)

    
    def test_get_ZKE_encrypted_key_no_key(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.get_zke_enc.return_value = None
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 404)
    

    def test_get_ZKE_blocked_user(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.getUserByID.return_value = User(id=1, isBlocked=True, isVerified=True, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_get_ZKE_unverified_user(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.getUserByID.return_value = User(id=1, isBlocked=False, isVerified=False, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)