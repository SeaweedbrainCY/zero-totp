import unittest
from app import app
from database.db import db 
from environment import conf
from zero_totp_db_model.model import User as UserModel
from unittest.mock import patch
import datetime
from database.user_repo import User as User_repo
from database.totp_secret_repo import TOTP_secret as TOTP_secret_repo
from database.zke_repo import ZKE as ZKE_encryption_key_repo
from database.google_drive_integration_repo import GoogleDriveIntegration as GoogleDriveIntegration_repo
from database.preferences_repo import Preferences as Preferences_repo
from database.oauth_tokens_repo import Oauth_tokens as Oauth_tokens_repo
from zero_totp_db_model.model  import Preferences as PreferencesModel
from database.session_token_repo import SessionTokenRepo 
from CryptoClasses import refresh_token as refresh_token_crypto_utility
from uuid import uuid4
from environment import conf


class TestDeleteAccount(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.deleteEndpoint = "/api/v1/account"
        
        
        self.full_user_id =1
        self.user_without_google_drive = 2
        self.user_blocked = 5
        self.user_not_verified = 6
        self.user_admin_id = 7

        self.user_repo = User_repo()
        self.totp_secret_repo = TOTP_secret_repo()
        self.zke_encryption_key_repo = ZKE_encryption_key_repo()
        self.google_drive_integration_repo = GoogleDriveIntegration_repo()
        self.preferences_repo = Preferences_repo()
        self.oauth_tokens_repo = Oauth_tokens_repo()
        self.session_token_repo = SessionTokenRepo()

        self.delete_google_drive_option = patch("controllers.delete_google_drive_option").start()
        self.delete_google_drive_option.return_value = True
        self.delete_google_drive_backup = patch("controllers.delete_google_drive_backup").start()
        self.delete_google_drive_backup.return_value = True

        self.checkpw = patch("CryptoClasses.hash_func.Bcrypt.checkpw").start()
        self.checkpw.return_value = True

        



        with self.flask_application.app.app_context():
            db.create_all()
            self.user_repo.create("user1", "user1@test.com", "password", "salt", "salt", "01/01/2001", isVerified=True, isBlocked=False)
            self.user_repo.create("user2", "user2@test.com", "password", "salt", "salt", "01/01/2001", isVerified=True, isBlocked=False)
            self.user_repo.create("user3", "user3@test.com", "password", "salt", "salt", "01/01/2001", isVerified=True, isBlocked=False)
            self.user_repo.create("user4", "user4@test.com", "password", "salt", "salt", "01/01/2001", isVerified=True, isBlocked=False)
            self.user_repo.create("user5", "user5@test.com", "password", "salt", "salt", "01/01/2001", isVerified=True, isBlocked=True)
            self.user_repo.create("user6", "user6@test.com", "password", "salt", "salt", "01/01/2001", isVerified=False, isBlocked=False)
            self.user_repo.create("user7", "user7@test.com", "password", "salt", "salt", "01/01/2001", isVerified=True, isBlocked=False, role="admin")

            # User 1 :
            self.totp_secret_repo.add(self.full_user_id, "secret1", str(uuid4()))
            self.totp_secret_repo.add(self.full_user_id, "secret2", str(uuid4()))
            self.totp_secret_repo.add(self.full_user_id, "secret3", str(uuid4()))
            self.totp_secret_repo.add(self.full_user_id, "secret4", str(uuid4()))
            self.zke_encryption_key_repo.create(self.full_user_id, "zke1")
            self.google_drive_integration_repo.create(self.full_user_id, True)
            self.preferences_repo.create_default_preferences(self.full_user_id)
            self.oauth_tokens_repo.add(self.full_user_id, "enc_creds", "expiry", "nonce", "tag")

            # User 2 :
            self.totp_secret_repo.add(self.user_without_google_drive, "secret1", str(uuid4()))
            self.totp_secret_repo.add(self.user_without_google_drive, "secret2", str(uuid4()))
            self.totp_secret_repo.add(self.user_without_google_drive, "secret3", str(uuid4()))
            self.totp_secret_repo.add(self.user_without_google_drive, "secret4", str(uuid4()))
            self.zke_encryption_key_repo.create(self.full_user_id, "zke1")

            _, self.full_user_session_token = self.session_token_repo.generate_session_token(self.full_user_id)
            _, self.user_without_google_drive_session_token = self.session_token_repo.generate_session_token(self.user_without_google_drive)
            _, self.user_blocked_session_token = self.session_token_repo.generate_session_token(self.user_blocked)
            _, self.user_not_verified_session_token = self.session_token_repo.generate_session_token(self.user_not_verified)
            _, self.user_admin_session_token = self.session_token_repo.generate_session_token(self.user_admin_id)

            refresh_token_crypto_utility.generate_refresh_token(self.full_user_id, self.full_user_session_token)
            refresh_token_crypto_utility.generate_refresh_token(self.user_without_google_drive, self.user_without_google_drive_session_token)
            refresh_token_crypto_utility.generate_refresh_token(self.user_blocked, self.user_blocked_session_token)
            refresh_token_crypto_utility.generate_refresh_token(self.user_not_verified, self.user_not_verified_session_token)
            refresh_token_crypto_utility.generate_refresh_token(self.user_admin_id, self.user_admin_session_token)
            
            
            db.session.commit()
    

    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()


##############################
## delete account as a user ##
##############################



    def test_delete_user_with_google_drive(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"session-token" :self.full_user_session_token}
            self.client.headers = {"x-hash-passphrase": "passphrase"}
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 200)
            self.delete_google_drive_backup.assert_called_once_with({"user":self.full_user_id}, self.full_user_id, {"user":self.full_user_id})
            self.delete_google_drive_option.assert_called_once_with({"user":self.full_user_id}, self.full_user_id, {"user":self.full_user_id})
            self.assertEqual(self.user_repo.getById(self.full_user_id), None)
            self.assertEqual(self.totp_secret_repo.get_all_enc_secret_by_user_id(self.full_user_id), [])
            self.assertEqual(self.zke_encryption_key_repo.getByUserId(self.full_user_id), None)
            self.assertEqual(self.google_drive_integration_repo.get_by_user_id(self.full_user_id), None)
            self.assertEqual(db.session.query(PreferencesModel).filter_by(user_id=self.full_user_id).first() , None)
            self.assertEqual(self.oauth_tokens_repo.get_by_user_id(self.full_user_id), None)
    
    def test_delete_user_without_google_drive(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"session-token" :self.user_without_google_drive_session_token}
            self.client.headers = {"x-hash-passphrase": "passphrase"}
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 200)
            self.delete_google_drive_backup.assert_called_once_with({"user":self.user_without_google_drive}, self.user_without_google_drive, {"user":self.user_without_google_drive})
            self.delete_google_drive_option.assert_called_once_with({"user":self.user_without_google_drive}, self.user_without_google_drive, {"user":self.user_without_google_drive})
            self.assertEqual(self.user_repo.getById(self.user_without_google_drive), None)
            self.assertEqual(self.totp_secret_repo.get_all_enc_secret_by_user_id(self.user_without_google_drive), [])
            self.assertEqual(self.zke_encryption_key_repo.getByUserId(self.user_without_google_drive), None)
            self.assertEqual(self.google_drive_integration_repo.get_by_user_id(self.user_without_google_drive), None)
            self.assertEqual(db.session.query(PreferencesModel).filter_by(user_id=self.user_without_google_drive).first() , None)
            self.assertEqual(self.oauth_tokens_repo.get_by_user_id(self.user_without_google_drive), None)
    
    def test_delete_admin(self):
         with self.flask_application.app.app_context():
            self.client.cookies= {"session-token" :self.user_admin_session_token}
            self.client.headers = {"x-hash-passphrase": "passphrase"}
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 403, f'Expected 403, got {response.status_code}. Response: {response.json()}')
            self.assertEqual(response.json(),  {"message": "Admin cannot be deleted"})
            self.delete_google_drive_backup.assert_not_called()
            self.delete_google_drive_option.assert_not_called()
            self.assertNotEqual(self.user_repo.getById(self.user_admin_id), None)
            
    def test_delete_bad_passphrase(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"session-token" :self.full_user_session_token}
            self.client.headers = {"x-hash-passphrase": "badPassphrase"}
            self.checkpw.return_value = False
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 403)
            self.assertNotEqual(self.user_repo.getById(self.full_user_id), None)
    
    def test_delete_no_passphrase_header(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"session-token" :self.full_user_session_token}
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 401)
            self.assertNotEqual(self.user_repo.getById(self.full_user_id), None)

    def test_delete_user_doesnt_exists(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"session-token" :str(uuid4())}
            self.client.headers = {"x-hash-passphrase": "badPassphrase"}
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 403)
            self.assertNotEqual(self.user_repo.getById(self.full_user_id), None)
    
    def test_delete_user_error_with_google_drive(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"session-token" :self.full_user_session_token}
            self.client.headers = {"x-hash-passphrase": "passphrase"}
            self.delete_google_drive_backup.side_effect = Exception("error")
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.user_repo.getById(self.full_user_id), None)
            self.assertEqual(self.totp_secret_repo.get_all_enc_secret_by_user_id(self.full_user_id), [])
            self.assertEqual(self.zke_encryption_key_repo.getByUserId(self.full_user_id), None)
            self.assertEqual(self.google_drive_integration_repo.get_by_user_id(self.full_user_id), None)
            self.assertEqual(db.session.query(PreferencesModel).filter_by(user_id=self.full_user_id).first() , None)
            self.assertEqual(self.oauth_tokens_repo.get_by_user_id(self.full_user_id), None)


    def test_delete_user_error_while_deleting_from_db(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"session-token" :self.full_user_session_token}
            self.client.headers = {"x-hash-passphrase": "passphrase"}
            self.secrets_delete_all = patch("database.totp_secret_repo.TOTP_secret.delete_all").start()
            self.secrets_delete_all.side_effect = Exception("error")
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 500)
    
    def test_delete_user_not_verified(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"session-token" :self.user_not_verified_session_token}
            self.client.headers = {"x-hash-passphrase": "passphrase"}
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 403)
            self.assertNotEqual(self.user_repo.getById(self.user_not_verified), None)
    
    def test_delete_user_blocked(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"session-token" :self.user_blocked_session_token}
            self.client.headers = {"x-hash-passphrase": "passphrase"}
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 403)
            self.assertNotEqual(self.user_repo.getById(self.user_blocked), None)

