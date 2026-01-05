import unittest
from app import app
import controllers
from unittest.mock import patch
from database.user_repo import User as UserRepo
from database.oauth_tokens_repo import Oauth_tokens as OAuthTokensRepo
from database.google_drive_integration_repo import GoogleDriveIntegration as GoogleDriveIntegrationRepo
from database.zke_repo import ZKE as ZKERepo
from database.totp_secret_repo import TOTP_secret as TotpSecretRepo
from database.session_token_repo import SessionTokenRepo
from environment import conf
import datetime
from database.db import db
from CryptoClasses.encryption import ServiceSideEncryption
from uuid import uuid4
import base64
import json
from Utils import utils

class TestGoogleDriveBackup(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.client = self.application.test_client()
        self.endpoint = "/api/v1/google-drive/backup"
        self.blocked_user_id = 2
        self.unverified_user_id = 3


        self.google_drive_backup = patch("Oauth.google_drive_api.backup").start()
        self.google_drive_backup.return_value = True
        self.google_drive_clean = patch("Oauth.google_drive_api.clean_backup_retention").start()
        self.google_drive_clean.return_value = True

        self.delete_all_backups = patch("Oauth.google_drive_api.delete_all_backups").start()
        self.delete_all_backups.return_value = True

        self.user_repo = UserRepo()
        self.google_integration = GoogleDriveIntegrationRepo()
        self.oauth_token = OAuthTokensRepo()
        self.sse = ServiceSideEncryption()
        self.zke_key = ZKERepo()
        self.secrets_repo = TotpSecretRepo()
        self.session_repo = SessionTokenRepo()

        self.creds = {"creds": "creds", "expiry":datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")}
        creds_b64 = base64.b64encode(json.dumps(self.creds).encode("utf-8")).decode("utf-8")
        encrypted_creds = self.sse.encrypt(creds_b64)
        with self.application.app.app_context():
            db.create_all()
            user = self.user_repo.create(username="user1", email="user1@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.utcnow())
            blocked_user = self.user_repo.create(username="user2", email="user2@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.utcnow(), isBlocked=True)
            unverified_user = self.user_repo.create(username="user3", email="user3@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=False, today=datetime.datetime.utcnow(), isBlocked=False)
            self.zke_key.create(user_id=1, encrypted_key="encrypted_key")
            self.google_integration.create(user_id=1, google_drive_sync=True)
            self.oauth_token.add(user_id=1, enc_credentials=encrypted_creds["ciphertext"], expires_at=self.creds["expiry"], nonce=encrypted_creds["nonce"], tag=encrypted_creds["tag"])


            for i in range(20):
                self.secrets_repo.add(user_id=1, enc_secret=f"enc_secret{i}", uuid=str(uuid4()))
            db.session.commit()

            self.session_token_user_1,_ = utils.generate_new_session(user=user, ip_address=None)
            self.session_token_user_blocked,_ = utils.generate_new_session(user=blocked_user, ip_address=None)
            self.session_token_user_unverified,_ = utils.generate_new_session(user=unverified_user, ip_address=None)

            


    def tearDown(self):
        patch.stopall()
        with self.application.app.app_context():
            db.session.remove()
            db.drop_all()
    
    

######
## PUT
######
    def test_google_drive_backup(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_1}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 201)
            self.google_drive_backup.assert_called_once()
            self.google_drive_clean.assert_called_once()
    
    def test_google_drive_backup_no_oauth_token(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_1}
            self.oauth_token.delete(user_id=1)
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_google_drive_backup_option_disable(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_1}
            self.google_integration.update_google_drive_sync(user_id=1, google_drive_sync=False)
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
            
    def test_google_drive_backup_bad_credentials(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_1}
            self.oauth_token.update(user_id=1, enc_credentials="bad_credentials", tag="bad_tag", nonce="bad_nonce", expires_at=datetime.datetime.utcnow())
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 500)
    
    def test_google_drive_backup_error_while_backuping(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_1}
            backup = patch("Oauth.google_drive_api.backup").start()
            backup.side_effect = Exception("error")
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 500)
    
    def test_google_drive_backup_error_while_cleaning(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_1}
            backup = patch("Oauth.google_drive_api.clean_backup_retention").start()
            backup.side_effect = Exception("error")
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 500)
    
    def test_google_drive_blocked_user(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_blocked}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "User is blocked")
    
    def test_google_drive_unverified_user(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_unverified}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "Not verified")
    

    def test_google_drive_backup_when_tenant_disabled(self):
        with self.application.app.app_context():
            with patch.object(conf.features.google_drive, 'enabled', False):
                self.client.cookies = {'session-token': self.session_token_user_1}
                response = self.client.put(self.endpoint)
                self.assertEqual(response.status_code, 403)
                self.assertEqual(response.json()["message"], "Google drive sync is not enabled on this tenant.")

    



#########
## DELETE
#########

    def test_google_drive_delete_all_backup(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_1}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.delete_all_backups.assert_called_once()
    
    def test_google_drive_delete_all_failed(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_1}
            self.delete_all_backups.return_value = False
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 500)
        
    def test_google_drive_delete_all_backup_no_oauth_token(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_1}
            self.oauth_token.delete(user_id=1)
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_google_drive_delete_all_backup_option_disable(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_1}
            self.google_integration.update_google_drive_sync(user_id=1, google_drive_sync=False)
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_google_drive_delete_all_backup_no_option(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_1}
            self.get_google_drive_integration = patch("database.google_drive_integration_repo.GoogleDriveIntegration.get_by_user_id").start()
            self.get_google_drive_integration.return_value = None
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 403)

    def test_google_drive_delete_all_backup_bad_credentials(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_1}
            self.oauth_token.update(user_id=1, enc_credentials="bad_credentials", tag="bad_tag", nonce="bad_nonce", expires_at=datetime.datetime.utcnow())
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 500)
    
    def test_google_drive_delete_all_backup_error_while_deleting(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_1}
            backup = patch("Oauth.google_drive_api.delete_all_backups").start()
            backup.side_effect = Exception("error")
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 500)

    
    def test_delete_google_drive_blocked_user(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_blocked}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "User is blocked")
    
    def test_delete_google_drive_unverified_user(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_unverified}
            response = self.client.delete(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "Not verified")

    def test_google_drive_delete_all_backup_when_tenant_disabled(self):
        with self.application.app.app_context():
            with patch.object(conf.features.google_drive, 'enabled', False):
                self.client.cookies = {'session-token': self.session_token_user_1}
                response = self.client.delete(self.endpoint)
                self.assertEqual(response.status_code, 403)
                self.assertEqual(response.json()["message"], "Google drive sync is not enabled on this tenant.")


    
