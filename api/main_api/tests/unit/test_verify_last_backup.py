import unittest
import controllers
from app import app
from unittest.mock import patch
from db_repo.user_repo import User as UserRepo
from db_repo.oauth_tokens_repo import Oauth_tokens as OAuthTokensRepo
from db_repo.google_drive_integration_repo import GoogleDriveIntegration as GoogleDriveIntegrationRepo
from db_repo.zke_repo import ZKE as ZKERepo
from db_repo.totp_secret_repo import TOTP_secret as TotpSecretRepo
from environment import conf
from CryptoClasses import jwt_func
import jwt
import datetime
from db_models.db import db
from CryptoClasses.encryption import ServiceSideEncryption
from uuid import uuid4
import base64
import json
from Utils import utils

class TestGoogleDriveVerifyLastBackup(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.application.test_client()
        self.endpoint = "/google-drive/last-backup/verify"
        self.user_id = 1
        self.blocked_user_id = 2
        self.unverified_user_id = 3


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
            self.zke_key.create(user_id=1, encrypted_key="encrypted_key")
            self.google_integration.create(user_id=1, google_drive_sync=True)
            self.oauth_token.add(user_id=1, enc_credentials=encrypted_creds["ciphertext"], expires_at=self.creds["expiry"], nonce=encrypted_creds["nonce"], tag=encrypted_creds["tag"])

            for i in range(20):
                self.secrets_repo.add(user_id=1, enc_secret=f"enc_secret{i}", uuid=str(uuid4()))
            
            tmp_client = self.application.test_client()
            tmp_client.cookies = {"api-key": self.jwtCookie}
            export_vault_b64 = tmp_client.get("/vault/export").json().split(",")[0]
            self.exported_vault = json.loads(base64.b64decode(export_vault_b64))
        self.get_checksum = patch("Oauth.google_drive_api.get_last_backup_checksum").start()
        self.get_checksum.return_value = self.exported_vault["secrets_sha256sum"], datetime.datetime.utcnow().strftime("%Y-%m-%d")


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
    
    def test_google_drive_verify_last_backup(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "ok")
            self.assertEqual(response.json()["last_backup_date"], datetime.datetime.utcnow().strftime("%Y-%m-%d"))
            self.assertEqual(response.json()["is_up_to_date"], True)
            self.get_checksum.assert_called_once()
            self.google_drive_backup.assert_not_called()
            self.google_drive_clean.assert_called_once()

    def test_google_drive_verify_last_backup_no_up_to_date(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            self.secrets_repo.add(user_id=1, enc_secret="new-secret", uuid=str(uuid4()))
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "ok")
            self.assertIn("last_backup_date", response.json())
            self.assertEqual(response.json()["is_up_to_date"], False)
            self.get_checksum.assert_called_once()
            self.google_drive_backup.assert_not_called()
            self.google_drive_clean.assert_not_called()
    
    def test_google_verify_last_backup_corrupted_files(self):
         with self.application.app.app_context():
              self.client.cookies = {"api-key": self.jwtCookie}
              self.get_checksum.side_effect = utils.CorruptedFile("error")
              response = self.client.get(self.endpoint)
              self.assertEqual(response.status_code, 200)
              self.assertEqual(response.json()["status"], "corrupted_file")
    
    def test_google_verify_last_backup_file_not_found(self):
         with self.application.app.app_context():
              self.client.cookies = {"api-key": self.jwtCookie}
              self.get_checksum.side_effect = utils.FileNotFound("error")
              response = self.client.get(self.endpoint)
              self.assertEqual(response.status_code, 404)
              self.assertEqual(response.json()["error"], "file_not_found")


    def test_google_verify_last_backup_no_oauth_token(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            self.oauth_token.delete(user_id=1)
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_google_verify_last_backup_option_disable(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            self.google_integration.update_google_drive_sync(user_id=1, google_drive_sync=False)
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
            
    def test_google_drive_backup_bad_credentials(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            self.oauth_token.update(user_id=1, enc_credentials="bad_credentials", tag="bad_tag", nonce="bad_nonce", expires_at=datetime.datetime.utcnow())
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 500)
    
    
    def test_google_verify_no_cookie(self):
        with self.application.app.app_context():
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 401)

    
    def test_google_drive_verify_bad_cookie(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": "badcookie"}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)

    def test_google_drive_verify_blocked(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": jwt_func.generate_jwt(self.blocked_user_id)}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_google_drive_verify_unverified(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": jwt_func.generate_jwt(self.unverified_user_id)}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
   