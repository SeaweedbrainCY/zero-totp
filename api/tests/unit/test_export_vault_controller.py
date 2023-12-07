import unittest
import controllers
from app import app
from unittest.mock import patch
from database.model import User, TOTP_secret, ZKE_encryption_key
import environment as env
from CryptoClasses import jwt_func
from CryptoClasses.sign_func import API_signature
import jwt
import datetime
import base64
import json

class TestAllSecret(unittest.TestCase):

    def setUp(self):
        if env.db_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.application.test_client()
        self.endpoint = "/vault/export"

        self.get_user = patch("database.user_repo.User.getById").start()
        self.get_user.return_value = User(id=1, derivedKeySalt="salt", isBlocked=False, isVerified=True, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")

        self.get_zke_key = patch("database.zke_repo.ZKE.getByUserId").start()
        self.get_zke_key.return_value = ZKE_encryption_key(ZKE_key="key")

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
    

    def test_export_vault(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 200)
        self.get_user.assert_called()
        self.get_zke_key.assert_called_once()
        self.get_all_secret.assert_called_once()
        export_data = response.json()
        self.assertEqual(len(export_data.split(',')), 2)
        vault_json_string = base64.b64decode(export_data.split(',')[0]).decode("utf-8")
        signature = export_data.split(',')[1]
        self.assertTrue(API_signature().verify_rsa_signature(signature, export_data.split(',')[0]))
        vault = json.loads(vault_json_string)
        self.assertTrue(vault["version"])
        if vault["version"] == 1:
            self.assertTrue(vault["date"])
            self.assertTrue(vault["secrets"])
            self.assertTrue(vault["derived_key_salt"])
            self.assertTrue(vault["zke_key_enc"])
            self.assertTrue(vault["secrets_sha256sum"])
        else :
            raise Exception("Unknown vault version")

    def test_export_vault_no_cookie(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 401)

    def test_export_vault_bad_cookie(self):
        self.client.cookies = {"api-key":"bad_cookie"}
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_export_vault_expired_cookie(self):
        self.client.cookies = {"api-key": self.generate_expired_cookie()}
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)

    
    def test_export_vault_user_not_found(self):
        self.get_user.return_value = None
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 401)
    
    def test_export_vault_no_zke_key(self):
        self.get_zke_key.return_value = None
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 404)
    
    def test_export_vault_user_blocked(self):
        self.get_user.return_value = User(id=1, derivedKeySalt="salt", isBlocked=True, isVerified=True, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], "User is blocked")
    
    def test_export_vault_user_not_verified(self):
        self.get_user.return_value = User(id=1, derivedKeySalt="salt", isBlocked=False, isVerified=False, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], "Not verified")



