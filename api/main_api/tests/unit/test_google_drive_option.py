import unittest
import main_api.controllers as controllers
from main_api.app import app
from unittest.mock import patch
from main_api.db_repo.user_repo import User as UserRepo
from main_api.db_repo.oauth_tokens_repo import Oauth_tokens as OAuthTokensRepo
from main_api.db_repo.google_drive_integration_repo import GoogleDriveIntegration as GoogleDriveIntegrationRepo
from main_api.environment import conf
from main_api.CryptoClasses import jwt_func
import jwt
import datetime
from db_models.db import db
from main_api.CryptoClasses.encryption import ServiceSideEncryption
import base64
import json
from uuid import uuid4

class TestGoogleDriveOption(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.application.test_client()
        self.endpoint = "/google-drive/option"
        self.blocked_user_id = 2
        self.not_blocked_user_id = 3

        self.google_api_revoke_creds = patch("Oauth.google_drive_api.revoke_credentials").start()
        self.google_api_revoke_creds.return_value = True


        self.user_repo = UserRepo()
        self.google_integration = GoogleDriveIntegrationRepo()
        self.oauth_token = OAuthTokensRepo()
        self.sse = ServiceSideEncryption()
        self.creds = {"creds": "creds", "expiry":datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")}
        creds_b64 = base64.b64encode(json.dumps(self.creds).encode("utf-8")).decode("utf-8")
        encrypted_creds = self.sse.encrypt(creds_b64)
        with self.application.app.app_context():
            db.create_all()
            self.user_repo.create(username="user", email="user@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.utcnow())
            self.user_repo.create(username="user", email="user@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.utcnow(), isBlocked=True)
            self.user_repo.create(username="user", email="user@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=False, today=datetime.datetime.utcnow())

            
            self.oauth_token.add(user_id=1, enc_credentials=encrypted_creds["ciphertext"], expires_at=self.creds["expiry"], nonce=encrypted_creds["nonce"], tag=encrypted_creds["tag"])

            
            

    def tearDown(self):
        patch.stopall()
        with self.application.app.app_context():
            db.session.remove()
            db.drop_all()
    
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

#########
## GET ##
#########

    def test_google_drive_option(self):
        with self.application.app.app_context():
            self.google_integration.create(user_id=1, google_drive_sync=True)
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "enabled")

    def test_google_drive_option_disabled(self):
        with self.application.app.app_context():
            self.google_integration.create(user_id=1, google_drive_sync=False)
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "disabled")

    def test_google_drive_option_doesnt_exists(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "disabled")
    
    def test_google_drive_no_cookie(self):
        with self.application.app.app_context():
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 401)

    def test_google_drive_bad_cookie(self):
         with self.application.app.app_context():
            self.client.cookies = {"api-key": "badcookie"}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_google_drive_blocked_user(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": jwt_func.generate_jwt(self.blocked_user_id)}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "User is blocked")
    
    def test_google_drive_unverified_user(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": jwt_func.generate_jwt(self.not_blocked_user_id)}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "Not verified")

   
############
## DELETE ##
############

    def test_google_drive_option_delete(self):
        with self.application.app.app_context():
            self.google_integration.create(user_id=1, google_drive_sync=True)
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["message"], "Google drive sync disabled")
            self.google_api_revoke_creds.assert_called_once()
            self.assertEqual(self.google_integration.is_google_drive_enabled(1),0)
            self.assertIsNone(self.oauth_token.get_by_user_id(1))
            self.assertIsNone(self.oauth_token.get_by_user_id(1))


    def test_google_drive_option_delete_decryption_failed(self):
        with self.application.app.app_context():
            self.google_integration.create(user_id=1, google_drive_sync=True)
            self.oauth_token.update(user_id=1, enc_credentials="bad_credentials", tag="bad_tag", nonce="bad_nonce", expires_at=datetime.datetime.utcnow())
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["message"], "Error while decrypting credentials")
            self.assertEqual(self.google_integration.is_google_drive_enabled(1),0)
            self.assertIsNone(self.oauth_token.get_by_user_id(1))

    def test_google_drive_option_delete_no_oauth_token(self):
        with self.application.app.app_context():
            self.google_integration.create(user_id=1, google_drive_sync=True)
            self.oauth_token.delete(user_id=1)
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["message"],  "Google drive sync is not enabled")
            self.assertEqual(self.google_integration.is_google_drive_enabled(1),0)
            self.assertIsNone(self.oauth_token.get_by_user_id(1))
    
    def test_google_drive_option_delete_option_disable(self):
         with self.application.app.app_context():
            self.google_integration.create(user_id=1, google_drive_sync=False)
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["message"], "Google drive sync disabled")
            self.google_api_revoke_creds.assert_called_once()
            self.assertEqual(self.google_integration.is_google_drive_enabled(1),0)
            self.assertIsNone(self.oauth_token.get_by_user_id(1))

    
    def test_google_drive_delete_option_option_doesnt_exists(self):
         with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["message"], "Google drive sync disabled")
            self.assertEqual(self.google_integration.is_google_drive_enabled(1),0)
            self.assertIsNone(self.oauth_token.get_by_user_id(1))
    
    def test_google_drive_option_delete_revoke_exception(self):
        with self.application.app.app_context():
            self.google_integration.create(user_id=1, google_drive_sync=True)
            self.google_api_revoke_creds.side_effect = Exception("error")
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["message"], "Error while revoking credentials")
            self.google_api_revoke_creds.assert_called_once()
            self.assertEqual(self.google_integration.is_google_drive_enabled(1),0)
            self.assertIsNone(self.oauth_token.get_by_user_id(1))
    
    def test_google_drive_option_delete_no_cookie(self):
        with self.application.app.app_context():
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 401)
        
    def test_google_drive_option_delete_bad_cookie(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": "badcookie"}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_google_drive_option_delete_blocked_user(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": jwt_func.generate_jwt(self.blocked_user_id)}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "User is blocked")
    
    def test_google_drive_option_delete_unverified_user(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": jwt_func.generate_jwt(self.not_blocked_user_id)}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "Not verified")