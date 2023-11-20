import unittest
import controllers
from app import app
from unittest.mock import patch
from database.model import User, TOTP_secret
import environment as env
from CryptoClasses import jwt_func
import jwt
import datetime

class TestUpdateEmail(unittest.TestCase):

    def setUp(self):
        if env.db_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.application.test_client()
        self.endpoint = "/update/email"
        

        self.update_email = patch("database.user_repo.User.update_email").start()
        self.update_email.return_value = User(id=1)

        self.getUserByEmail = patch("database.user_repo.User.getByEmail").start()
        self.getUserByEmail.return_value = None 

        self.check_email = patch("Utils.utils.check_email").start()
        self.check_email.return_value = True

        self.payload = {"email" : "test@test.com"}


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
    
    def test_update_email(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 201)
        self.update_email.assert_called_once()
    
    def test_update_email_no_cookie(self):
        response = self.client.put(self.endpoint)
        self.assertEqual(response.status_code, 401)
    
    def test_update_email_bad_cookie(self):
        self.client.cookies = {"api-key": "badcookie"}
        response = self.client.put(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_update_email_expired_jwt(self):
        self.client.cookies = {"api-key": self.generate_expired_cookie()}
        response = self.client.put(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_update_email_bad_format(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.check_email.return_value = False
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 400)
    
    def test_update_email_already_used(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.getUserByEmail.return_value = True
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 403)
    
    def test_update_email_error_db(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.update_email.return_value = False
        response = self.client.put(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 500)

    
