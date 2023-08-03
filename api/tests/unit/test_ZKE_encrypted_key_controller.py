import unittest
import controllers
from app import create_app
from unittest.mock import patch
from database.model import ZKE_encryption_key
import environment as env
from Crypto import jwt_func
import jwt
import datetime

class TestZKEEncryptedKey(unittest.TestCase):

    def setUp(self):
        env.db_uri = "sqlite:///:memory:"
        self.app = create_app()
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.app.test_client()
        self.endpoint = "/zke_encrypted_key"
        

        self.get_zke_enc = patch("database.zke_repo.ZKE.getByUserId").start()
        self.get_zke_enc.return_value = ZKE_encryption_key(id=1, user_id=1, ZKE_key="encrypted_key")


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
    
    def test_get_ZKE_encrypted_key(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertIn("zke_encrypted_key", response.json)
        self.get_zke_enc.assert_called_once()
    
    def test_get_ZKE_encrypted_key_no_cookie(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 401)
    
    def test_get_ZKE_encrypted_key_bad_cookie(self):
        self.client.set_cookie("localhost", "api-key","badcookie")
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_get_ZKE_encrypted_key_expired_jwt(self):
        self.client.set_cookie("localhost", "api-key",self.generate_expired_cookie())
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)

    
    def test_get_ZKE_encrypted_key_no_key(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        self.get_zke_enc.return_value = None
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 404)