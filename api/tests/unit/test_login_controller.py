import unittest
import controllers
from app import app
from unittest.mock import patch
from database.model import User
import environment as env

class TestLoginController(unittest.TestCase):

    def setUp(self):
        if env.db_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.client = self.application.test_client()
        self.loginEndpoint = "/login"
        self.specsEndpoint = "/login/specs?username=test@test.fr"


        self.getByEmailMocked = patch("database.user_repo.User.getByEmail").start()
        self.getByEmailMocked.return_value = User(id=1, username="username", derivedKeySalt="randomSalt", password="hashed", isVerified=1, passphraseSalt="salt", isBlocked=False)

        self.get_is_google_drive_enabled = patch("database.google_drive_integration_repo.GoogleDriveIntegration.is_google_drive_enabled").start()
        self.get_is_google_drive_enabled.return_value = False

        self.checkpw = patch("CryptoClasses.hash_func.Bcrypt.checkpw").start()
        self.checkpw.return_value = True

        self.check_email = patch("Utils.utils.check_email").start()
        self.check_email.return_value = True 

        self.json_payload = {"email" : "test@test.com", "password": "Abcdefghij1#"}

    def tearDown(self):
        patch.stopall()
    

    def test_login(self):
        response = self.client.post(self.loginEndpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.json())
        self.assertIn("id", response.json())
        self.assertIn("derivedKeySalt", response.json())
        self.assertIn("isGoogleDriveSync", response.json())
        self.assertIn("role", response.json())
        self.assertIn("isVerified", response.json())
        self.assertIn("Set-Cookie", response.headers)
        self.assertIn("api-key", response.headers["Set-Cookie"])
        self.assertIn("HttpOnly", response.headers["Set-Cookie"])
        self.assertIn("Secure", response.headers["Set-Cookie"])
        self.assertIn("SameSite=Lax", response.headers["Set-Cookie"])
        self.assertIn("Expires", response.headers["Set-Cookie"])
    
    def test_login_not_verified_user(self):
        response = self.client.post(self.loginEndpoint, json=self.json_payload)
        self.getByEmailMocked.return_value = User(id=1, username="username", derivedKeySalt="randomSalt", password="hashed", isVerified=0, passphraseSalt="salt", isBlocked=False)
        self.assertEqual(response.status_code, 200)
        self.assertIn("isVerified", response.json())
        self.assertIn("Set-Cookie", response.headers)

    def test_login_missing_parameters(self):
        for key in self.json_payload.keys():
            json_payload = self.json_payload.copy()
            del json_payload[key]
            response = self.client.post(self.loginEndpoint, json=json_payload)
            self.assertEqual(response.status_code, 400)
        
        for key in self.json_payload.keys():
            json_payload = self.json_payload.copy()
            json_payload[key]=""
            response = self.client.post(self.loginEndpoint, json=json_payload)
            self.assertEqual(response.status_code, 400)
    
    def test_login_forbidden_email(self):
        self.check_email.return_value = False
        response = self.client.post(self.loginEndpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
    
    
    def test_login_no_user(self):
        self.getByEmailMocked.return_value = None 
        response = self.client.post(self.loginEndpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
        self.checkpw.assert_called_once()
        self.assertEqual(response.json()["message"], "generic_errors.invalid_creds") #translation key
    

    def test_login_bad_passphrase(self):
        self.checkpw.return_value = False
        response = self.client.post(self.loginEndpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
        self.checkpw.assert_called_once()
        self.assertEqual(response.json()["message"], "generic_errors.invalid_creds")
    
    def test_login_as_blocked_user(self):
        self.getByEmailMocked.return_value =  User(id=1, username="username", derivedKeySalt="randomSalt", password="hashed", isVerified=1, passphraseSalt="salt", isBlocked=True)
        response = self.client.post(self.loginEndpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["message"], "blocked") # key for the frontend
        self.assertNotIn("Set-Cookie", response.headers)
    
    def test_login_as_blocked_user_with_bad_passphrase(self):
        self.getByEmailMocked.return_value =  User(id=1, username="username", derivedKeySalt="randomSalt", password="hashed", isVerified=1, passphraseSalt="salt", isBlocked=True)
        self.checkpw.return_value = False
        response = self.client.post(self.loginEndpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn("Set-Cookie", response.headers)
        self.assertEqual(response.json()["message"], "generic_errors.invalid_creds")


    def test_login_specs(self):
        response = self.client.get(self.specsEndpoint)
        self.assertEqual(response.status_code, 200)
        self.assertIn("passphrase_salt", response.json())
    
    def test_login_specs_bad_email(self):
        self.check_email.return_value = False
        response = self.client.get(self.specsEndpoint)
        self.assertEqual(response.status_code, 400)
        
        response = self.client.get("/login/specs")
        self.assertEqual(response.status_code, 400)

    
    def test_login_specs_no_user(self):
        self.getByEmailMocked = None 
        response = self.client.get(self.specsEndpoint)
        self.assertEqual(response.status_code, 200)
        self.assertIn("passphrase_salt", response.json())
    

    
    
