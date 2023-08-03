import unittest
import controllers
from app import create_app
from unittest.mock import patch
from database.model import User, TOTP_secret
import environment as env
from Crypto import jwt_func
import jwt
import datetime

class TestAllSecret(unittest.TestCase):

    def setUp(self):
        env.db_uri = "sqlite:///:memory:"
        self.app = create_app()
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.app.test_client()
        self.endpoint = "/all_secrets"
        

        self.get_all_secret = patch("database.totp_secret_repo.TOTP_secret.get_all_enc_secret_by_user_id").start()
        self.get_all_secret.return_value = [TOTP_secret(uuid="uuid", user_id=1, secret_enc = "enc_secret"), TOTP_secret(uuid="uuid", user_id=1, secret_enc = "enc_secret2")]


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
    

    def test_get_all_secret(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 200)
        self.get_all_secret.assert_called_once()
    
    def test_get_all_secret_no_cookie(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 401)
    
    def test_get_all_secret_bad_cookie(self):
        self.client.set_cookie("localhost", "api-key", "badcookie")
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_get_all_secret_expired_jwt(self):
        self.client.set_cookie("localhost", "api-key", self.generate_expired_cookie())
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_get_all_secret_no_secret(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        self.get_all_secret.return_value = []
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 404)