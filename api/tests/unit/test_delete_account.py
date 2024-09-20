import unittest
from app import app
from database.db import db 
from environment import conf
from zero_totp_db_model.model import User as UserModel
from unittest.mock import patch
from CryptoClasses.jwt_func import generate_jwt, ISSUER as jwt_ISSUER, ALG as jwt_ALG
import datetime
import jwt
from database.user_repo import User as User_repo
from database.totp_secret_repo import TOTP_secret as TOTP_secret_repo
from database.zke_repo import ZKE as ZKE_encryption_key_repo
from database.google_drive_integration_repo import GoogleDriveIntegration as GoogleDriveIntegration_repo
from database.preferences_repo import Preferences as Preferences_repo
from database.oauth_tokens_repo import Oauth_tokens as Oauth_tokens_repo
from database.admin_repo import Admin as Admin_repo
from zero_totp_db_model.model import Admin as AdminModel, Preferences as PreferencesModel
from uuid import uuid4
from environment import conf


class TestDeleteAccount(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.deleteEndpoint = "/api/v1/account"
        self.adminDeleteEndpoint = "/admin/account"
        
        
        self.full_user_id =1
        self.user_without_google_drive = 2
        self.user_admin_id = 3
        self.user_admin_id2 = 4
        self.user_blocked = 5
        self.user_not_verified = 6

        self.user_repo = User_repo()
        self.totp_secret_repo = TOTP_secret_repo()
        self.zke_encryption_key_repo = ZKE_encryption_key_repo()
        self.google_drive_integration_repo = GoogleDriveIntegration_repo()
        self.preferences_repo = Preferences_repo()
        self.oauth_tokens_repo = Oauth_tokens_repo()
        self.admin_repo = Admin_repo()

        self.delete_google_drive_option = patch("controllers.delete_google_drive_option").start()
        self.delete_google_drive_option.return_value = True
        self.delete_google_drive_backup = patch("controllers.delete_google_drive_backup").start()
        self.delete_google_drive_backup.return_value = True

        self.checkpw = patch("CryptoClasses.hash_func.Bcrypt.checkpw").start()
        self.checkpw.return_value = True

        if conf.features.admins.admin_can_delete_users == True:
            raise Exception("ADMIN_CAN_DELETE_USERS environment should be false by default")
        conf.features.admins.admin_can_delete_users = True
        



        with self.flask_application.app.app_context():
            db.create_all()
            self.user_repo.create("user1", "user1@test.com", "password", "salt", "salt", "01/01/2001", isVerified=True, isBlocked=False)
            self.user_repo.create("user2", "user2@test.com", "password", "salt", "salt", "01/01/2001", isVerified=True, isBlocked=False)
            self.user_repo.create("user3", "user3@test.com", "password", "salt", "salt", "01/01/2001", isVerified=True, isBlocked=False)
            self.user_repo.create("user4", "user3@test.com", "password", "salt", "salt", "01/01/2001", isVerified=True, isBlocked=False)
            self.user_repo.create("user5", "user5@test.com", "password", "salt", "salt", "01/01/2001", isVerified=True, isBlocked=True)
            self.user_repo.create("user6", "user6@test.com", "password", "salt", "salt", "01/01/2001", isVerified=False, isBlocked=False)

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
            
            # User 3:
            self.totp_secret_repo.add(self.user_admin_id, "secret1", str(uuid4()))
            self.totp_secret_repo.add(self.user_admin_id, "secret2", str(uuid4()))
            self.totp_secret_repo.add(self.user_admin_id, "secret3", str(uuid4()))
            self.totp_secret_repo.add(self.user_admin_id, "secret4", str(uuid4()))
            self.zke_encryption_key_repo.create(self.user_admin_id, "zke1")
            self.user_repo.update_role(self.user_admin_id, "admin")
            self.user_repo.update_role(self.user_admin_id2, "admin")
            admin_token = AdminModel(user_id=self.user_admin_id, token_hashed="token", token_expiration=(datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).timestamp())
            db.session.add(admin_token)
            db.session.commit()
    

    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()
        conf.features.admins.admin_can_delete_users = False


##############################
## delete account as a user ##
##############################



    def test_delete_user_with_google_drive(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.full_user_id)}
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
            self.client.cookies= {"api-key" :generate_jwt(self.user_without_google_drive)}
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
            self.client.cookies= {"api-key" :generate_jwt(self.user_admin_id)}
            self.client.headers = {"x-hash-passphrase": "passphrase"}
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 403)
            self.delete_google_drive_backup.assert_not_called()
            self.delete_google_drive_option.assert_not_called()
            self.assertNotEqual(self.user_repo.getById(self.user_admin_id), None)
            self.assertNotEqual(self.totp_secret_repo.get_all_enc_secret_by_user_id(self.user_admin_id), [])
            self.assertNotEqual(self.zke_encryption_key_repo.getByUserId(self.user_admin_id), None)

    def test_delete_bad_passphrase(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.full_user_id)}
            self.client.headers = {"x-hash-passphrase": "badPassphrase"}
            self.checkpw.return_value = False
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 403)
            self.assertNotEqual(self.user_repo.getById(self.full_user_id), None)
    
    def test_delete_no_passphrase_header(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.full_user_id)}
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 401)
            self.assertNotEqual(self.user_repo.getById(self.full_user_id), None)
    
    def test_delete_no_cookie(self):
        with self.flask_application.app.app_context():
            self.client.headers = {"x-hash-passphrase": "badPassphrase"}
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 401)
    
    def test_bad_cookie(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key":"badCookie"}
            self.client.headers = {"x-hash-passphrase": "badPassphrase"}
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 403)
            self.assertNotEqual(self.user_repo.getById(self.full_user_id), None)

    def test_delete_user_doesnt_exists(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(10)}
            self.client.headers = {"x-hash-passphrase": "badPassphrase"}
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 401)
            self.assertNotEqual(self.user_repo.getById(self.full_user_id), None)
    
    def test_delete_user_error_with_google_drive(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.full_user_id)}
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
            self.client.cookies= {"api-key" :generate_jwt(self.full_user_id)}
            self.client.headers = {"x-hash-passphrase": "passphrase"}
            self.secrets_delete_all = patch("database.totp_secret_repo.TOTP_secret.delete_all").start()
            self.secrets_delete_all.side_effect = Exception("error")
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 500)
    
    def test_delete_user_not_verified(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.user_not_verified)}
            self.client.headers = {"x-hash-passphrase": "passphrase"}
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 403)
            self.assertNotEqual(self.user_repo.getById(self.user_not_verified), None)
    
    def test_delete_user_blocked(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.user_blocked)}
            self.client.headers = {"x-hash-passphrase": "passphrase"}
            response = self.client.delete(self.deleteEndpoint)
            self.assertEqual(response.status_code, 403)
            self.assertNotEqual(self.user_repo.getById(self.user_blocked), None)

##############################
## delete account an admin  ##
##############################

    def test_delete_as_admin(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.user_admin_id), "admin-api-key":generate_jwt(self.user_admin_id, admin=True)}
            response = self.client.delete(self.adminDeleteEndpoint + "/" + str(self.full_user_id))
            self.assertEqual(response.status_code, 200)
            self.delete_google_drive_backup.assert_called_once_with({"user":self.full_user_id}, self.full_user_id, {"user":self.full_user_id})
            self.delete_google_drive_option.assert_called_once_with({"user":self.full_user_id}, self.full_user_id, {"user":self.full_user_id})
            self.assertEqual(self.user_repo.getById(self.full_user_id), None)
            self.assertEqual(self.totp_secret_repo.get_all_enc_secret_by_user_id(self.full_user_id), [])
            self.assertEqual(self.zke_encryption_key_repo.getByUserId(self.full_user_id), None)
            self.assertEqual(self.google_drive_integration_repo.get_by_user_id(self.full_user_id), None)
            self.assertEqual(db.session.query(PreferencesModel).filter_by(user_id=self.full_user_id).first() , None)
            self.assertEqual(self.oauth_tokens_repo.get_by_user_id(self.full_user_id), None)
            self.assertNotEqual(self.user_repo.getById(self.user_admin_id), None)

    def test_delete_as_admin_but_not_admin(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.full_user_id), "admin-api-key":generate_jwt(self.full_user_id, admin=True)}
            response = self.client.delete(self.adminDeleteEndpoint + "/" + str(self.user_without_google_drive))
            self.assertEqual(response.status_code, 403)
            self.assertNotEqual(self.user_repo.getById(self.user_without_google_drive), None)
    
    def test_delete_as_admin_but_not_admin_cookie(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.user_admin_id)}
            response = self.client.delete(self.adminDeleteEndpoint + "/" + str(self.full_user_id))
            self.assertEqual(response.status_code, 403)
            self.assertNotEqual(self.user_repo.getById(self.full_user_id), None)
    
    def test_delete_as_admin_but_not_admin_cookie_and_not_admin(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.user_without_google_drive)}
            response = self.client.delete(self.adminDeleteEndpoint + "/" + str(self.full_user_id))
            self.assertEqual(response.status_code, 403)
            self.assertNotEqual(self.user_repo.getById(self.full_user_id), None)
    
    def test_delete_as_admin_bad_admin_cookie(self):
         with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.user_admin_id), "admin-api-key":generate_jwt(self.full_user_id, admin=False)}
            response = self.client.delete(self.adminDeleteEndpoint + "/" + str(self.full_user_id))
            self.assertEqual(response.status_code, 403)
            self.assertNotEqual(self.user_repo.getById(self.full_user_id), None)
    
    def test_delete_as_admin_no_cookie(self):
        with self.flask_application.app.app_context():
            response = self.client.delete(self.adminDeleteEndpoint + "/" + str(self.full_user_id))
            self.assertEqual(response.status_code, 401)
            self.assertNotEqual(self.user_repo.getById(self.full_user_id), None)
    
    def test_delete_as_admin_bad_cookie(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :"badCookie", "admin-api-key":generate_jwt(self.user_admin_id, admin=True)}
            response = self.client.delete(self.adminDeleteEndpoint + "/" + str(self.full_user_id))
            self.assertEqual(response.status_code, 403)
            self.assertNotEqual(self.user_repo.getById(self.full_user_id), None)
    
    def test_delete_as_admin_user_doesnt_exists(self):
         with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.user_admin_id), "admin-api-key":generate_jwt(self.user_admin_id, admin=True)}
            response = self.client.delete(self.adminDeleteEndpoint + "/" + str(1000))
            self.assertEqual(response.status_code, 404)
    
    def test_delete_as_admin_but_user_id_admin(self):
         with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.user_admin_id), "admin-api-key":generate_jwt(self.user_admin_id, admin=True)}
            response = self.client.delete(self.adminDeleteEndpoint + "/" + str(self.user_admin_id2))
            self.assertEqual(response.status_code, 403)
    
    def test_delete_as_admin_not_google_drive_user(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.user_admin_id), "admin-api-key":generate_jwt(self.user_admin_id, admin=True)}
            response = self.client.delete(self.adminDeleteEndpoint + "/" + str(self.user_without_google_drive))
            self.assertEqual(response.status_code, 200)
            self.delete_google_drive_backup.assert_called_once_with({"user":self.user_without_google_drive}, self.user_without_google_drive, {"user":self.user_without_google_drive})
            self.delete_google_drive_option.assert_called_once_with({"user":self.user_without_google_drive}, self.user_without_google_drive, {"user":self.user_without_google_drive})
            self.assertEqual(self.user_repo.getById(self.user_without_google_drive), None)
            self.assertEqual(self.totp_secret_repo.get_all_enc_secret_by_user_id(self.user_without_google_drive), [])
            self.assertEqual(self.zke_encryption_key_repo.getByUserId(self.user_without_google_drive), None)
            self.assertEqual(self.google_drive_integration_repo.get_by_user_id(self.user_without_google_drive), None)
            self.assertEqual(db.session.query(PreferencesModel).filter_by(user_id=self.user_without_google_drive).first() , None)
            self.assertEqual(self.oauth_tokens_repo.get_by_user_id(self.user_without_google_drive), None)
            self.assertNotEqual(self.user_repo.getById(self.user_admin_id), None)
    

    def test_delete_as_admin_but_admin_are_forbidden(self):
        conf.features.admins.admin_can_delete_users = False
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.user_admin_id), "admin-api-key":generate_jwt(self.user_admin_id, admin=True)}
            response = self.client.delete(self.adminDeleteEndpoint + "/" + str(self.user_without_google_drive))
            self.assertEqual(response.status_code, 403)