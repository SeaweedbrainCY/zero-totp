import unittest
import controllers
from app import app
from unittest.mock import patch
from database.user_repo import User as UserRepo
from database.oauth_tokens_repo import Oauth_tokens as OAuthTokensRepo
from database.google_drive_integration_repo import GoogleDriveIntegration as GoogleDriveIntegrationRepo
import environment as env
from CryptoClasses import jwt_func
import jwt
import datetime
from database.db import db
from CryptoClasses.encryption import ServiceSideEncryption
from base64 import b64decode
import json

class TestOauthCallback(unittest.TestCase):

    def setUp(self):
        if env.db_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.application.test_client()
        self.creds = {"secret" : "secret_should_be_encrypted", "expiry": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")}
        self.endpoint = "/google-drive/oauth/callback"
        self.setSateSession = "/google-drive/oauth/authorization-flow"

        self.get_auth_url = patch("Oauth.oauth_flow.get_authorization_url").start()
        self.get_auth_url.return_value = "auth_url", 'state'

        

        self.get_credentials = patch("Oauth.oauth_flow.get_credentials").start()
        self.get_credentials.return_value = self.creds
        self.user_repo = UserRepo()
        self.google_integration_repo = GoogleDriveIntegrationRepo()
        self.sse = ServiceSideEncryption()
        self.oauth_tokens = OAuthTokensRepo()
        with self.application.app.app_context():
            db.create_all()
            self.user_repo.create(username="user", email="user@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.utcnow())
            db.session.commit()
            


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
        jwtCookie = jwt.encode(payload, env.jwt_secret, algorithm=jwt_func.ALG)
        return jwtCookie
    

    def test_oauth_callback_no_token_yet(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            self.client.get(self.setSateSession)
            self.client.follow_redirects = False
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 302)
            self.assertIn(env.frontend_URI[0] , response.headers["Location"])
            self.assertNotIn("error", response.headers["Location"])
            encrypted_credentials = self.oauth_tokens.get_by_user_id(1)
            self.assertIsNotNone(encrypted_credentials.enc_credentials)
            self.assertNotIn(self.creds["secret"], encrypted_credentials.enc_credentials)
            self.assertEqual(self.creds, json.loads(b64decode(self.sse.decrypt(encrypted_credentials.enc_credentials,encrypted_credentials.cipher_tag, encrypted_credentials.cipher_nonce))))
            self.assertEqual(self.google_integration_repo.is_google_drive_enabled(1), 1)
    
    def test_oauth_callback_no_creds(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        self.get_credentials.return_value = None
        with self.application.app.app_context():
            self.client.get(self.setSateSession)
            self.client.follow_redirects = False
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 302)
            self.assertIn(env.frontend_URI[0] , response.headers["Location"])
            self.assertIn("error", response.headers["Location"])

    def test_oauth_callback_already_token(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        with self.application.app.app_context():
            self.oauth_tokens.add(1, "creds", "date","tag", "nonce")
            self.client.get(self.setSateSession)
            self.client.follow_redirects = False
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 302)
            self.assertIn(env.frontend_URI[0] , response.headers["Location"])
            self.assertNotIn("error", response.headers["Location"])
            encrypted_credentials = self.oauth_tokens.get_by_user_id(1)
            self.assertIsNotNone(encrypted_credentials.enc_credentials)
            self.assertNotIn(self.creds["secret"], encrypted_credentials.enc_credentials)
            self.assertEqual(self.creds, json.loads(b64decode(self.sse.decrypt(encrypted_credentials.enc_credentials,encrypted_credentials.cipher_tag, encrypted_credentials.cipher_nonce))))
            self.assertEqual(self.google_integration_repo.is_google_drive_enabled(1), 1)

    def test_oauth_callback_already_synched(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        with self.application.app.app_context():
            self.oauth_tokens.add(1, "creds", "date","tag", "nonce")
            self.google_integration_repo.create(1, 1)
            self.client.get(self.setSateSession)
            self.client.follow_redirects = False
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 302)
            self.assertIn(env.frontend_URI[0] , response.headers["Location"])
            self.assertNotIn("error", response.headers["Location"])
            encrypted_credentials = self.oauth_tokens.get_by_user_id(1)
            self.assertIsNotNone(encrypted_credentials.enc_credentials)
            self.assertNotIn(self.creds["secret"], encrypted_credentials.enc_credentials)
            self.assertEqual(self.creds, json.loads(b64decode(self.sse.decrypt(encrypted_credentials.enc_credentials,encrypted_credentials.cipher_tag, encrypted_credentials.cipher_nonce))))
            self.assertEqual(self.google_integration_repo.is_google_drive_enabled(1), 1)
        

    def test_oauth_callback_exception(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        with self.application.app.app_context():
            google_get_by_userid = patch("database.google_drive_integration_repo.GoogleDriveIntegration.get_by_user_id").start()
            google_get_by_userid.side_effect = Exception("test")
            self.client.get(self.setSateSession)
            self.client.follow_redirects = False
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 302)
            self.assertIn(env.frontend_URI[0] , response.headers["Location"])
            self.assertIn("error", response.headers["Location"])
            encrypted_credentials = self.oauth_tokens.get_by_user_id(1)
            self.assertIsNotNone(encrypted_credentials.enc_credentials)
            self.assertNotIn(self.creds["secret"], encrypted_credentials.enc_credentials)
            self.assertEqual(self.google_integration_repo.is_google_drive_enabled(1), 0)
        
    def test_oauth_callback_add_token_error(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        with self.application.app.app_context():
            add_token = patch("database.oauth_tokens_repo.Oauth_tokens.add").start()
            add_token.return_value = None
            self.client.get(self.setSateSession)
            self.client.follow_redirects = False
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 302)
            self.assertIn(env.frontend_URI[0] , response.headers["Location"])
            self.assertIn("error", response.headers["Location"])
            encrypted_credentials = self.oauth_tokens.get_by_user_id(1)
            self.assertIsNone(encrypted_credentials)
            self.assertEqual(self.google_integration_repo.is_google_drive_enabled(1), 0)
        
    def test_oauth_callback_no_flask_session(self):
        self.client.cookies = {"api-key": self.jwtCookie}
        with self.application.app.app_context():
            add_token = patch("database.oauth_tokens_repo.Oauth_tokens.add").start()
            add_token.return_value = None
            self.client.follow_redirects = False
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 302)
            self.assertIn(env.frontend_URI[0] , response.headers["Location"])
            self.assertIn("error", response.headers["Location"])
            encrypted_credentials = self.oauth_tokens.get_by_user_id(1)
            self.assertIsNone(encrypted_credentials)
            self.assertEqual(self.google_integration_repo.is_google_drive_enabled(1), 0)
    
    def test_oauth_callback_no_cookie(self):
        with self.application.app.app_context():
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(self.google_integration_repo.is_google_drive_enabled(1), 0)