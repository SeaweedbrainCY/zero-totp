import unittest
import controllers
from app import create_app
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
        env.db_uri = "sqlite:///:memory:"
        self.app = create_app()
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.app.test_client()
        self.creds = {"secret" : "secret_should_be_encrypted", "expiry": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}
        self.endpoint = "/google-drive/oauth/callback"

        self.get_credentials = patch("Oauth.oauth_flow.get_credentials").start()
        self.get_credentials.return_value = self.creds
        self.user_repo = UserRepo()
        self.google_integration_repo = GoogleDriveIntegrationRepo()
        self.sse = ServiceSideEncryption()
        self.oauth_tokens = OAuthTokensRepo()
        with self.app.app_context():
            db.create_all()
            self.user_repo.create(username="user", email="user@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now())
            db.session.commit()
            


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
    

    def test_oauth_callback_no_token_yet(self):
        self.client.set_cookie("localhost", "api-key", self.jwtCookie)
        with self.app.app_context():
            with self.client.session_transaction() as session:
                session["state"] = "state"
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 302)
            self.assertIn(env.frontend_URI[0] , response.headers["Location"])
            self.assertNotIn("error", response.headers["Location"])
            encrypted_credentials = self.oauth_tokens.get_by_user_id(1)
            self.assertIsNotNone(encrypted_credentials.enc_credentials)
            self.assertNotIn(self.creds["secret"], encrypted_credentials.enc_credentials)
            self.assertEqual(self.creds, json.loads(b64decode(self.sse.decrypt(encrypted_credentials.enc_credentials,encrypted_credentials.cipher_tag, encrypted_credentials.cipher_nonce))))
            self.assertEqual(self.google_integration_repo.is_google_drive_enabled(1), 1)


        

        
    
   