import unittest
from app import app
from database.db import db
import controllers
from unittest.mock import patch
from zero_totp_db_model.model import User, TOTP_secret
from environment import conf
from CryptoClasses import jwt_func
import jwt
import datetime

class TestAllSecret(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.application.test_client()
        self.endpoint = "/api/v1/all_secrets"
        with self.application.app.app_context():
            db.create_all()
            db.session.commit()
        

        self.get_all_secret = patch("database.totp_secret_repo.TOTP_secret.get_all_enc_secret_by_user_id").start()
        self.get_all_secret.return_value = [TOTP_secret(uuid="uuid", user_id=1, secret_enc = "enc_secret"), TOTP_secret(uuid="uuid", user_id=1, secret_enc = "enc_secret2")]

        self.getUserById = patch("database.user_repo.User.getById").start()
        self.getUserById.return_value = User(id=1, isBlocked=False, isVerified=True, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")


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
    

    def test_get_all_secret(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 200)
        self.get_all_secret.assert_called_once()
    
    def test_get_all_secret_no_cookie(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 401)
    
    def test_get_all_secret_bad_cookie(self):
        self.client.cookies = {"api-key": "badcookie"}
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_get_all_secret_expired_jwt(self):
        self.client.cookies = {"api-key": self.generate_expired_cookie()}
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 401)
    
    def test_get_all_secret_no_secret(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.get_all_secret.return_value = []
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 404)

    
    def test_get_all_secret_blocked_user(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.getUserById.return_value = User(id=1, isBlocked=True, isVerified=True, mail="mail", password="password", role="user", username="username", createdAt="01/01/2001")
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], "User is blocked")
    
    def test_get_all_secret_unverified_user(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.getUserById.return_value = User(id=1, isBlocked=False, isVerified=False, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], "Not verified")