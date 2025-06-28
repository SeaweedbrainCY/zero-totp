from app import app
import unittest
import controllers
from unittest.mock import patch
from database.user_repo import User as UserRepo
from database.oauth_tokens_repo import Oauth_tokens as OAuthTokensRepo
from database.google_drive_integration_repo import GoogleDriveIntegration as GoogleDriveIntegrationRepo
from database.zke_repo import ZKE as ZKERepo
from database.totp_secret_repo import TOTP_secret as TotpSecretRepo
from environment import conf
from database.session_token_repo import SessionTokenRepo
import datetime
from database.db import db
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
        self.client = self.application.test_client()
        self.endpoint = "/api/v1/google-drive/last-backup/verify"
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
        self.session_token_repo = SessionTokenRepo()


        self.creds = {"creds": "creds","refresh_token":"fake_token", "expiry":datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")}
        creds_b64 = base64.b64encode(json.dumps(self.creds).encode("utf-8")).decode("utf-8")
        encrypted_creds = self.sse.encrypt(creds_b64)
        with self.application.app.app_context():
            db.create_all()
            self.user_repo.create(username="user1", email="user1@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.utcnow())
            self.user_repo.create(username="user2", email="user2@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.utcnow(), isBlocked=True)
            self.user_repo.create(username="user3", email="user3@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=False, today=datetime.datetime.utcnow())
            self.zke_key.create(user_id=1, encrypted_key="encrypted_key")
            self.google_integration.create(user_id=1, google_drive_sync=True)
            self.oauth_token.add(user_id=1, enc_credentials=encrypted_creds["ciphertext"], expires_at=self.creds["expiry"], nonce=encrypted_creds["nonce"], tag=encrypted_creds["tag"])

            for i in range(20):
                self.secrets_repo.add(user_id=1, enc_secret=f"enc_secret{i}", uuid=str(uuid4()))
                
            _, self.session_token = self.session_token_repo.generate_session_token(self.user_id)
            _, self.blocked_user_session = self.session_token_repo.generate_session_token(self.blocked_user_id)
            _, self.unverified_user_session = self.session_token_repo.generate_session_token(self.unverified_user_id)


            tmp_client = self.application.test_client()
            tmp_client.cookies = {"session-token": self.session_token}
            export_vault_b64 = tmp_client.get("/api/v1/vault/export").json().split(",")[0]
            self.exported_vault = json.loads(base64.b64decode(export_vault_b64))

            

        self.get_checksum = patch("Oauth.google_drive_api.get_last_backup_checksum").start()
        self.get_checksum.return_value = self.exported_vault["secrets_sha256sum"], datetime.datetime.utcnow().strftime("%Y-%m-%d")


    def tearDown(self):
        patch.stopall()
        with self.application.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_google_drive_verify_last_backup(self):
        with self.application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
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
            self.client.cookies = {"session-token": self.session_token}
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
              self.client.cookies = {"session-token": self.session_token}
              self.get_checksum.side_effect = utils.CorruptedFile("error")
              response = self.client.get(self.endpoint)
              self.assertEqual(response.status_code, 200)
              self.assertEqual(response.json()["status"], "corrupted_file")
    
    def test_google_verify_last_backup_file_not_found(self):
         with self.application.app.app_context():
              self.client.cookies = {"session-token": self.session_token}
              self.get_checksum.side_effect = utils.FileNotFound("error")
              response = self.client.get(self.endpoint)
              self.assertEqual(response.status_code, 404)
              self.assertEqual(response.json()["error"], "file_not_found")


    def test_google_verify_last_backup_no_oauth_token(self):
        with self.application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            self.oauth_token.delete(user_id=1)
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_google_verify_last_backup_option_disable(self):
        with self.application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            self.google_integration.update_google_drive_sync(user_id=1, google_drive_sync=False)
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
            
    def test_google_drive_backup_bad_credentials(self):
        with self.application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            self.oauth_token.update(user_id=1, enc_credentials="bad_credentials", tag="bad_tag", nonce="bad_nonce", expires_at=datetime.datetime.utcnow())
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 500)
    
    

    def test_google_drive_verify_blocked(self):
        with self.application.app.app_context():
            self.client.cookies = {"session-token": self.blocked_user_session}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_google_drive_verify_unverified(self):
        with self.application.app.app_context():
            self.client.cookies = {"session-token": self.unverified_user_session}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
   