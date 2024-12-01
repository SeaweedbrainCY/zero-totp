import unittest
from app import app
import controllers
from unittest.mock import patch
from database.user_repo import User as UserRepo
from database.oauth_tokens_repo import Oauth_tokens as OAuthTokensRepo
from database.google_drive_integration_repo import GoogleDriveIntegration as GoogleDriveIntegrationRepo
from environment import conf
import datetime
from database.db import db
from CryptoClasses.encryption import ServiceSideEncryption
import base64
import json
from uuid import uuid4
from database.session_token_repo import SessionTokenRepo

class TestGoogleDriveOption(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.client = self.application.test_client()
        self.endpoint = "/api/v1/google-drive/option"
        self.blocked_user_id = 2
        self.unverified_user_id = 3

        self.google_api_revoke_creds = patch("Oauth.google_drive_api.revoke_credentials").start()
        self.google_api_revoke_creds.return_value = True


        self.user_repo = UserRepo()
        self.google_integration = GoogleDriveIntegrationRepo()
        self.oauth_token = OAuthTokensRepo()
        self.sse = ServiceSideEncryption()
        self.session_repo = SessionTokenRepo()

        self.creds = {"creds": "creds", "expiry":datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S.%f")}
        creds_b64 = base64.b64encode(json.dumps(self.creds).encode("utf-8")).decode("utf-8")
        encrypted_creds = self.sse.encrypt(creds_b64)
        with self.application.app.app_context():
            db.create_all()
            self.user_repo.create(username="user1", email="user1@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now(datetime.UTC))
            self.user_repo.create(username="user2", email="user2@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now(datetime.UTC), isBlocked=True)
            self.user_repo.create(username="user3", email="user3@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=False, today=datetime.datetime.now(datetime.UTC))

            _, self.session_token_user_1 = self.session_repo.generate_session_token(1)
            _, self.session_token_user_blocked = self.session_repo.generate_session_token(self.blocked_user_id)
            _, self.session_token_user_unverified = self.session_repo.generate_session_token(self.unverified_user_id)

            
            self.oauth_token.add(user_id=1, enc_credentials=encrypted_creds["ciphertext"], expires_at=self.creds["expiry"], nonce=encrypted_creds["nonce"], tag=encrypted_creds["tag"])

            
            

    def tearDown(self):
        patch.stopall()
        with self.application.app.app_context():
            db.session.remove()
            db.drop_all()
    

#########
## GET ##
#########

    def test_google_drive_option(self):
        with self.application.app.app_context():
            self.google_integration.create(user_id=1, google_drive_sync=True)
            self.client.cookies = {'session-token': self.session_token_user_1}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "enabled")

    def test_google_drive_option_disabled(self):
        with self.application.app.app_context():
            self.google_integration.create(user_id=1, google_drive_sync=False)
            self.client.cookies = {'session-token': self.session_token_user_1}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "disabled")

    def test_google_drive_option_doesnt_exists(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_1}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "disabled")
    
    
    def test_google_drive_blocked_user(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_blocked}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "User is blocked")
    
    def test_google_drive_unverified_user(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_unverified}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "Not verified")

   
############
## DELETE ##
############

    def test_google_drive_option_delete(self):
        with self.application.app.app_context():
            self.google_integration.create(user_id=1, google_drive_sync=True)
            self.client.cookies = {'session-token': self.session_token_user_1}
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
            self.client.cookies = {'session-token': self.session_token_user_1}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["message"], "Error while decrypting credentials")
            self.assertEqual(self.google_integration.is_google_drive_enabled(1),0)
            self.assertIsNone(self.oauth_token.get_by_user_id(1))

    def test_google_drive_option_delete_no_oauth_token(self):
        with self.application.app.app_context():
            self.google_integration.create(user_id=1, google_drive_sync=True)
            self.oauth_token.delete(user_id=1)
            self.client.cookies = {'session-token': self.session_token_user_1}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["message"],  "Google drive sync is not enabled")
            self.assertEqual(self.google_integration.is_google_drive_enabled(1),0)
            self.assertIsNone(self.oauth_token.get_by_user_id(1))
    
    def test_google_drive_option_delete_option_disable(self):
         with self.application.app.app_context():
            self.google_integration.create(user_id=1, google_drive_sync=False)
            self.client.cookies = {'session-token': self.session_token_user_1}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["message"], "Google drive sync disabled")
            self.google_api_revoke_creds.assert_called_once()
            self.assertEqual(self.google_integration.is_google_drive_enabled(1),0)
            self.assertIsNone(self.oauth_token.get_by_user_id(1))

    
    def test_google_drive_delete_option_option_doesnt_exists(self):
         with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_1}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["message"], "Google drive sync disabled")
            self.assertEqual(self.google_integration.is_google_drive_enabled(1),0)
            self.assertIsNone(self.oauth_token.get_by_user_id(1))
    
    def test_google_drive_option_delete_revoke_exception(self):
        with self.application.app.app_context():
            self.google_integration.create(user_id=1, google_drive_sync=True)
            self.google_api_revoke_creds.side_effect = Exception("error")
            self.client.cookies = {'session-token': self.session_token_user_1}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["message"], "Error while revoking credentials")
            self.google_api_revoke_creds.assert_called_once()
            self.assertEqual(self.google_integration.is_google_drive_enabled(1),0)
            self.assertIsNone(self.oauth_token.get_by_user_id(1))
    
    def test_google_drive_option_delete_blocked_user(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_blocked}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "User is blocked")
    
    def test_google_drive_option_delete_unverified_user(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_unverified}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "Not verified")