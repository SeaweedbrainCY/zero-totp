import unittest
import controllers
from app import app
from unittest.mock import patch
from database.model import User, TOTP_secret
import environment as env
from CryptoClasses import jwt_func
import jwt
import datetime

class TestEncryptedSecretController(unittest.TestCase):
    USER_NOT_VERIFIED_ERROR_MESSAGE = "Not verified"
    USER_BLOCKED_ERROR_MESSAGE = "User is blocked"

    def setUp(self):
        if env.db_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.application.test_client()
        self.endpoint = "/encrypted_secret/uuid"
        

        self.getEncSecretByUUID = patch("database.totp_secret_repo.TOTP_secret.get_enc_secret_by_uuid").start()
        self.getEncSecretByUUID.return_value = TOTP_secret(uuid="uuid", user_id=1, secret_enc = "enc_secret")

        self.addTOTPSecret = patch("database.totp_secret_repo.TOTP_secret.add").start()
        self.addTOTPSecret.return_value =  TOTP_secret(uuid="uuid", user_id=1, secret_enc = "enc_secret")

        self.updateTOTPSecret = patch("database.totp_secret_repo.TOTP_secret.update_secret").start()
        self.addTOTPSecret.return_value =  TOTP_secret(uuid="uuid", user_id=1, secret_enc = "enc_secret")

        self.deleteTOTPSecret = patch("database.totp_secret_repo.TOTP_secret.delete").start()
        self.deleteTOTPSecret.return_value = TOTP_secret(uuid="uuid", user_id=1, secret_enc = "enc_secret")

        self.get_user_by_id = patch("database.user_repo.User.getById").start()
        self.get_user_by_id.return_value = User(id=1, isBlocked=False, isVerified=True, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")


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
    
######
## GET
######


    def test_get_encrypted_secret(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertIn("enc_secret", response.json())
    
    def test_get_encrypted_secret_no_cookie(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 401)
    
    def test_get_encrypted_secret_bad_cookie(self):
        self.client.cookies = {"api-key": "bad_cookie"}
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)

    def test_get_encrypted_secret_JWT_expired(self):
        jwtCookie = self.generate_expired_cookie()
        self.client.cookies = {"api-key": jwtCookie}
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_get_encrypted_secret_no_secret(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.getEncSecretByUUID.return_value = None
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
    

    def test_get_encrypted_secret_of_another_user(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.getEncSecretByUUID.return_value =  TOTP_secret(uuid="uuid", user_id=2, secret_enc = "enc_secret")
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)

    def test_get_encrypted_secret_user_blocked(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.get_user_by_id.return_value = User(id=1, isBlocked=True, isVerified=True, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], self.USER_BLOCKED_ERROR_MESSAGE)
    
    def test_get_encrypted_secret_user_unverified(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.get_user_by_id.return_value = User(id=1, isBlocked=False, isVerified=False, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], self.USER_NOT_VERIFIED_ERROR_MESSAGE)


#######
## POST
#######

    def test_post_encrypted_secret(self):
         self.client.cookies = {"api-key": self.jwtCookie}
         self.getEncSecretByUUID.return_value = None
         response = self.client.post(self.endpoint, json=self.json_payload)
         self.assertEqual(response.status_code, 201)
         self.addTOTPSecret.assert_called_once()
        
    def test_post_encrypted_secret_no_cookie(self):
        response = self.client.post(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 401)
    
    def test_post_encrypted_secret_bad_cookie(self):
        self.client.cookies = {"api-key": "bad_cookie"}
        response = self.client.post(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
    
    def test_post_encrypted_secret_JWT_expired(self):
        self.client.cookies = {"api-key": self.generate_expired_cookie()}
        response = self.client.post(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
    
    def test_post_encrypted_secret_secret_already_exists(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.post(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
    
    def test_post_encrypted_secret_error_db(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.getEncSecretByUUID.return_value = None
        self.addTOTPSecret.return_value = False
        response = self.client.post(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 500)
    
    def test_post_encrypted_secret_user_blocked(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.get_user_by_id.return_value = User(id=1, isBlocked=True, isVerified=True, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")
        response = self.client.post(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], self.USER_BLOCKED_ERROR_MESSAGE)
    
    def test_post_encrypted_secret_user_unverified(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.get_user_by_id.return_value = User(id=1, isBlocked=False, isVerified=False, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")
        response = self.client.post(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], self.USER_NOT_VERIFIED_ERROR_MESSAGE)

######
## PUT
######


    def test_update_encrypted_secret(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.put(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 201)
        self.updateTOTPSecret.assert_called_once()
    
    def test_update_encrypted_secret_no_cookie(self):
        response = self.client.put(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 401)
    
    def test_update_encrypted_secret_bad_cookie(self):
        self.client.cookies = {"api-key": "badCookie"}
        response = self.client.put(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
    
    def test_update_encrypted_secret_expired_cookie(self):
        self.client.cookies = {"api-key": self.generate_expired_cookie()}
        response = self.client.put(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
    
    def test_update_encrypted_secret_no_exists(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.getEncSecretByUUID.return_value = None
        response = self.client.put(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
    
    def test_update_encrypted_secret_wrong_user(self):
         self.client.cookies = {"api-key": self.jwtCookie}
         self.getEncSecretByUUID.return_value = TOTP_secret(uuid="uuid", user_id=2, secret_enc = "enc_secret")
         response = self.client.put(self.endpoint, json=self.json_payload)
         self.assertEqual(response.status_code, 403)
    
    def test_update_encrypted_secret_fail(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.updateTOTPSecret.return_value = None
        response = self.client.put(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 500)

    def test_update_encrypted_secret_user_blocked(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.get_user_by_id.return_value = User(id=1, isBlocked=True, isVerified=True, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")
        response = self.client.put(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], self.USER_BLOCKED_ERROR_MESSAGE)
    
    def test_update_encrypted_secret_user_unverified(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.get_user_by_id.return_value = User(id=1, isBlocked=False, isVerified=False, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")
        response = self.client.put(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], self.USER_NOT_VERIFIED_ERROR_MESSAGE)


#########
## DELETE
#########



    def test_delete_encrypted_secret(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 201)
        self.deleteTOTPSecret.assert_called_once()
    
    def test_delete_encrypted_secret_no_cookie(self):
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 401)
    
    def test_delete_encrypted_secret_bad_cookie(self):
        self.client.cookies = {"api-key": "badCookie"}
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_delete_encrypted_secret_expired_cookie(self):
        self.client.cookies = {'api-key': self.generate_expired_cookie()}
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_delete_encrypted_secret_no_exists(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.getEncSecretByUUID.return_value = None
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 403)
    

    def test_delete_encrypted_secret_wrong_user(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.getEncSecretByUUID.return_value = TOTP_secret(uuid="uuid", user_id=2, secret_enc = "enc_secret")
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 403)
    
    def test_delete_encrypted_secret_fail(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.deleteTOTPSecret.return_value = None
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 500)
    
    def test_delete_encrypted_secret_user_blocked(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.get_user_by_id.return_value = User(id=1, isBlocked=True, isVerified=True, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], self.USER_BLOCKED_ERROR_MESSAGE)
    
    def test_delete_encrypted_secret_user_unverified(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.get_user_by_id.return_value = User(id=1, isBlocked=False, isVerified=False, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001")
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], self.USER_NOT_VERIFIED_ERROR_MESSAGE)
