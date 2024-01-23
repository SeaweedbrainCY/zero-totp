import unittest
import controllers
from app import app
from unittest.mock import patch
from database.model import User, RateLimiting
import environment as env
from database.db import db 
import datetime

class TestLoginController(unittest.TestCase):

    def setUp(self):
        if env.db_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.client = self.application.test_client()
        self.loginEndpoint = "/login"
        self.specsEndpoint = "/login/specs?username=test@test.com"


        self.user1 = User(id=1, username="username", mail= "test@test.com",derivedKeySalt="randomSalt", password="hashed", isVerified=1, passphraseSalt="salt", isBlocked=False, createdAt="01/01/2001 01:01:01", role="user")
        with self.application.app.app_context():
            db.create_all()
            db.session.add(self.user1)
            db.session.commit()

        self.get_is_google_drive_enabled = patch("database.google_drive_integration_repo.GoogleDriveIntegration.is_google_drive_enabled").start()
        self.get_is_google_drive_enabled.return_value = False

        self.checkpw = patch("CryptoClasses.hash_func.Bcrypt.checkpw").start()
        self.checkpw.return_value = True

        self.check_email = patch("Utils.utils.check_email").start()
        self.check_email.return_value = True 

        self.get_ip = patch("Utils.utils.get_ip").start()
        self.get_ip.return_value = "1.1.1.1"

        self.json_payload = {"email" : "test@test.com", "password": "Abcdefghij1#"}

    def tearDown(self):
         with self.application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()
    

    

    def test_login(self):
        with self.application.app.app_context():
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
        with self.application.app.app_context():
            db.session.query(User).filter_by(id=1).update({"isVerified":False})
            db.session.commit()
            response = self.client.post(self.loginEndpoint, json=self.json_payload)
            self.assertEqual(response.status_code, 200)
            self.assertIn("isVerified", response.json())
            self.assertIn("Set-Cookie", response.headers)

    def test_login_missing_parameters(self):
        with self.application.app.app_context():
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
        with self.application.app.app_context():
            self.check_email.return_value = False
            response = self.client.post(self.loginEndpoint, json=self.json_payload)
            self.assertEqual(response.status_code, 403)
    
    
    def test_login_no_user(self):
        with self.application.app.app_context():
            payload = {"email" : "unknown@test.com", "password": "Abcdefghij1#"}
            response = self.client.post(self.loginEndpoint, json=payload)
            self.assertEqual(response.status_code, 403)
            self.checkpw.assert_called_once()
            self.assertEqual(response.json()["message"], "generic_errors.invalid_creds")    #translation key
    

    def test_login_bad_passphrase(self):
        with self.application.app.app_context():
            self.checkpw.return_value = False
            response = self.client.post(self.loginEndpoint, json=self.json_payload)
            self.assertEqual(response.status_code, 403)
            self.checkpw.assert_called_once()
            self.assertEqual(response.json()["message"], "generic_errors.invalid_creds")
    
    def test_login_as_blocked_user(self):
        with self.application.app.app_context():
            db.session.query(User).filter_by(id=1).update({"isBlocked":True})
            db.session.commit()
            response = self.client.post(self.loginEndpoint, json=self.json_payload)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["message"], "blocked") # key for the frontend
            self.assertNotIn("Set-Cookie", response.headers)

    def test_login_as_blocked_user_with_bad_passphrase(self):
        with self.application.app.app_context():
            db.session.query(User).filter_by(id=1).update({"isBlocked":True})
            db.session.commit()
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
        with self.application.app.app_context():
            response = self.client.get("/login/specs?username=unknown@test.com")
            self.assertEqual(response.status_code, 200)
            self.assertIn("passphrase_salt", response.json())

    
    def test_rate_limited_user(self):
        with self.application.app.app_context():
            self.checkpw.return_value = False
            for _ in range(env.login_attempts_limit_per_ip):
                response = self.client.post(self.loginEndpoint, json=self.json_payload)
                self.assertEqual(response.status_code, 403)
                self.assertEqual(response.json()["message"], "generic_errors.invalid_creds")
            response = self.client.post(self.loginEndpoint, json=self.json_payload)
            self.assertEqual(response.status_code, 429)
            self.assertEqual(response.json()["message"], "Too many requests")
            spec_response = self.client.get(self.specsEndpoint)
            self.assertEqual(spec_response.status_code, 429)
            self.assertEqual(spec_response.json()["message"], "Too many requests")
    
    def test_rate_limit_expiring(self):
        with self.application.app.app_context():
            for _ in range(env.login_attempts_limit_per_ip):
                attempt = RateLimiting(ip='1.1.1.1', user_id=None, action_type="failed_login", timestamp=datetime.datetime.utcnow() - datetime.timedelta(minutes=env.login_ban_time + 1))
                db.session.add(attempt)
                db.session.commit()
            self.checkpw.return_value = False
            response = self.client.post(self.loginEndpoint, json=self.json_payload)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["message"], "generic_errors.invalid_creds")
            self.checkpw.return_value = True
            response = self.client.post(self.loginEndpoint, json=self.json_payload)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(db.session.query(RateLimiting).filter_by(ip='1.1.1.1').all()), 0)
    
    def test_login_invalid_ip(self):
        with self.application.app.app_context():
            self.get_ip.return_value = None
            response = self.client.post(self.loginEndpoint, json=self.json_payload)
            self.assertEqual(response.status_code, 200)
            self.checkpw.assert_called_once()
    
    def test_login_private_ip(self):
        with self.application.app.app_context():
            self.get_ip.return_value = "127.0.0.1"
            response = self.client.post(self.loginEndpoint, json=self.json_payload)
            self.assertEqual(response.status_code, 200)
            self.checkpw.assert_called_once()

            

    
    
