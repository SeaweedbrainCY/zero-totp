import unittest
import controllers
from app import create_app
from unittest.mock import patch
from database.user_repo import User as UserRepo
from database.oauth_tokens_repo import Oauth_tokens as OAuthTokensRepo
from database.google_drive_integration_repo import GoogleDriveIntegration as GoogleDriveIntegrationRepo
from database.zke_repo import ZKE as ZKERepo
from database.totp_secret_repo import TOTP_secret as TotpSecretRepo
import environment as env
from CryptoClasses import jwt_func
import jwt
import datetime
from database.db import db
from CryptoClasses.encryption import ServiceSideEncryption
from uuid import uuid4
import base64
import json


class TestGoogleDriveBackup(unittest.TestCase):

    def setUp(self):
        env.db_uri = "sqlite:///:memory:"
        self.app = create_app().app
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.app.test_client()
        self.endpoint = "/google-drive/backup"


        self.google_drive_backup = patch("Oauth.google_drive_api.backup").start()
        self.google_drive_backup.return_value = True
        self.google_drive_clean = patch("Oauth.google_drive_api.clean_backup_retention").start()
        self.google_drive_clean.return_value = True

        self.user_repo = UserRepo()
        self.google_integration = GoogleDriveIntegrationRepo()
        self.oauth_token = OAuthTokensRepo()
        self.sse = ServiceSideEncryption()
        self.zke_key = ZKERepo()
        self.secrets_repo = TotpSecretRepo()
        self.creds = {"creds": "creds", "expiry":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}
        creds_b64 = base64.b64encode(json.dumps(self.creds).encode("utf-8")).decode("utf-8")
        encrypted_creds = self.sse.encrypt(creds_b64)
        with self.app.app_context():
            db.create_all()
            self.user_repo.create(username="user", email="user@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now())
            self.zke_key.create(user_id=1, encrypted_key="encrypted_key")
            self.google_integration.create(user_id=1, google_drive_sync=True)
            self.oauth_token.add(user_id=1, enc_credentials=encrypted_creds["ciphertext"], expires_at=self.creds["expiry"], nonce=encrypted_creds["nonce"], tag=encrypted_creds["tag"])

            for i in range(20):
                self.secrets_repo.add(user_id=1, enc_secret=f"enc_secret{i}", uuid=str(uuid4()))
            


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
    
    def test_google_drive_backup(self):
        with self.app.app_context():
            self.client.set_cookie("localhost", "api-key", self.jwtCookie)
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 201)
            self.google_drive_backup.assert_called_once()
            self.google_drive_clean.assert_called_once()
    
    def test_google_drive_backup_no_oauth_token(self):
        with self.app.app_context():
            self.client.set_cookie("localhost", "api-key", self.jwtCookie)
            self.oauth_token.delete(user_id=1)
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_google_drive_backup_option_disable(self):
        with self.app.app_context():
            self.client.set_cookie("localhost", "api-key", self.jwtCookie)
            self.google_integration.update_google_drive_sync(user_id=1, google_drive_sync=False)
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
            
    def test_google_drive_backup_bad_credentials(self):
        with self.app.app_context():
            self.client.set_cookie("localhost", "api-key", self.jwtCookie)
            self.oauth_token.update(user_id=1, enc_credentials="bad_credentials", tag="bad_tag", nonce="bad_nonce", expires_at=datetime.datetime.now())
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 500)
    
    def test_google_drive_backup_error_while_backuping(self):
        with self.app.app_context():
            self.client.set_cookie("localhost", "api-key", self.jwtCookie)
            backup = patch("Oauth.google_drive_api.backup").start()
            backup.side_effect = Exception("error")
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 500)
    
    def test_google_drive_backup_error_while_cleaning(self):
        with self.app.app_context():
            self.client.set_cookie("localhost", "api-key", self.jwtCookie)
            backup = patch("Oauth.google_drive_api.clean_backup_retention").start()
            backup.side_effect = Exception("error")
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 500)
    
    def test_google_drive_no_cookie(self):
        with self.app.app_context():
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 401)

    
    def test_google_drive_bad_cookie(self):
        with self.app.app_context():
            self.client.set_cookie("localhost", "api-key", "badcookie")
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)

   