import unittest
import controllers
from app import create_app
from unittest.mock import patch
from database.model import User, TOTP_secret
import environment as env
from CryptoClasses import jwt_func
import jwt
import datetime

class TestEncryptedSecretController(unittest.TestCase):

    def setUp(self):
        env.db_uri = "sqlite:///:memory:"
        self.app = create_app()
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.app.test_client()
        self.endpoint = "/encrypted_secret/uuid"
        

        self.getEncSecretByUUID = patch("database.totp_secret_repo.TOTP_secret.get_enc_secret_by_uuid").start()
        self.getEncSecretByUUID.return_value = TOTP_secret(uuid="uuid", user_id=1, secret_enc = "enc_secret")

        self.addTOTPSecret = patch("database.totp_secret_repo.TOTP_secret.add").start()
        self.addTOTPSecret.return_value =  TOTP_secret(uuid="uuid", user_id=1, secret_enc = "enc_secret")

        self.updateTOTPSecret = patch("database.totp_secret_repo.TOTP_secret.update_secret").start()
        self.addTOTPSecret.return_value =  TOTP_secret(uuid="uuid", user_id=1, secret_enc = "enc_secret")

        self.deleteTOTPSecret = patch("database.totp_secret_repo.TOTP_secret.delete").start()
        self.deleteTOTPSecret.return_value = TOTP_secret(uuid="uuid", user_id=1, secret_enc = "enc_secret")


        self.json_payload = {"enc_secret": "enc_secret"}

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
    

    def test_get_encrypted_secret(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertIn("enc_secret", response.json)
    
    def test_get_encrypted_secret_no_cookie(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 401)
    
    def test_get_encrypted_secret_bad_cookie(self):
        self.client.set_cookie("localhost", "api-key", "bad_cookie")
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)

    def test_get_encrypted_secret_JWT_expired(self):
        jwtCookie = self.generate_expired_cookie()
        self.client.set_cookie("localhost", "api-key", jwtCookie)
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_get_encrypted_secret_no_secret(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        self.getEncSecretByUUID.return_value = None
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
    

    def test_get_encrypted_secret_of_another_user(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        self.getEncSecretByUUID.return_value =  TOTP_secret(uuid="uuid", user_id=2, secret_enc = "enc_secret")
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
        

    def test_post_encrypted_secret(self):
         self.client.set_cookie("localhost", "api-key", self.jwtCookie)
         self.getEncSecretByUUID.return_value = None
         response = self.client.post(self.endpoint, json=self.json_payload)
         self.assertEqual(response.status_code, 201)
         self.addTOTPSecret.assert_called_once()
        
    def test_post_encrypted_secret_no_cookie(self):
        response = self.client.post(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 401)
    
    def test_post_encrypted_secret_bad_cookie(self):
        self.client.set_cookie("localhost", "api-key", "bad_cookie")
        response = self.client.post(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
    
    def test_post_encrypted_secret_JWT_expired(self):
        self.client.set_cookie("localhost", "api-key", self.generate_expired_cookie())
        response = self.client.post(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
    
    def test_post_encrypted_secret_secret_already_exists(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        response = self.client.post(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
    
    def test_post_encrypted_secret_error_db(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        self.getEncSecretByUUID.return_value = None
        self.addTOTPSecret.return_value = False
        response = self.client.post(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 500)
    

    def test_update_encrypted_secret(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        response = self.client.put(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 201)
        self.updateTOTPSecret.assert_called_once()
    
    def test_update_encrypted_secret_no_cookie(self):
        response = self.client.put(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 401)
    
    def test_update_encrypted_secret_bad_cookie(self):
        self.client.set_cookie("localhost", "api-key", "badCookie")
        response = self.client.put(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
    
    def test_update_encrypted_secret_expired_cookie(self):
        self.client.set_cookie("localhost", "api-key", self.generate_expired_cookie())
        response = self.client.put(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
    
    def test_update_encrypted_secret_no_exists(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        self.getEncSecretByUUID.return_value = None
        response = self.client.put(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
    
    def test_update_encrypted_secret_wrong_user(self):
         self.client.set_cookie("localhost", "api-key", self.jwtCookie)
         self.getEncSecretByUUID.return_value = TOTP_secret(uuid="uuid", user_id=2, secret_enc = "enc_secret")
         response = self.client.put(self.endpoint, json=self.json_payload)
         self.assertEqual(response.status_code, 403)
    
    def test_update_encrypted_secret_fail(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        self.updateTOTPSecret.return_value = None
        response = self.client.put(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 500)
    
    def test_delete_encrypted_secret(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 201)
        self.deleteTOTPSecret.assert_called_once()
    
    def test_delete_encrypted_secret_no_cookie(self):
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 401)
    
    def test_delete_encrypted_secret_bad_cookie(self):
        self.client.set_cookie("localhost", "api-key", "badCookie")
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_delete_encrypted_secret_expired_cookie(self):
        self.client.set_cookie("localhost", 'api-key', self.generate_expired_cookie())
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_delete_encrypted_secret_no_exists(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        self.getEncSecretByUUID.return_value = None
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 403)
    

    def test_delete_encrypted_secret_wrong_user(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        self.getEncSecretByUUID.return_value = TOTP_secret(uuid="uuid", user_id=2, secret_enc = "enc_secret")
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_delete_encrypted_secret_fail(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        self.deleteTOTPSecret.return_value = None
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 500)
    

