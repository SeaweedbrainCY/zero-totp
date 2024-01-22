import unittest
from app import app
from database.db import db 
import environment as env
from database.model import User as UserModel, RateLimiting
from unittest.mock import patch
from CryptoClasses.jwt_func import generate_jwt, ISSUER as jwt_ISSUER, ALG as jwt_ALG
import datetime
import jwt


class TestSendVerificationController(unittest.TestCase):

    def setUp(self):
        if env.db_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/email/send_verification"
        self.user_id = 1
        user = UserModel(id=self.user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role="admin")

        self.generate_new_email_verification_token = patch("Utils.utils.generate_new_email_verification_token", return_value="token").start()
        
        self.send_verification_email = patch("Email.send.send_verification_email", return_value=True).start()
        

        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(user)
            db.session.commit()
    
       
    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()

    def test_send_verification_email(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key": generate_jwt(self.user_id)}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.generate_new_email_verification_token.assert_called_once_with(user_id=self.user_id)
            self.send_verification_email.assert_called_once_with("user@user.com", "token")
    
    def test_send_verification_send_throw_error(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key": generate_jwt(self.user_id)}
            self.send_verification_email.side_effect = Exception("Error while sending email")
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 500)
    
    def test_send_verification_no_cookie(self):
        with self.flask_application.app.app_context():
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 401)
    
    def test_send_verification_bad_cookie(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key": "bad"}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_send_verification_rate_limited(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key": generate_jwt(self.user_id)}
            for _ in range(env.send_email_attempts_limit_per_user):
                response = self.client.get(self.endpoint)
                self.assertEqual(response.status_code, 200)
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 429)
    
    def test_rate_limiting_expired(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key": generate_jwt(self.user_id)}
            for _ in range(env.send_email_attempts_limit_per_user):
                attempt = RateLimiting(ip=None, user_id=self.user_id, action_type="send_verification_email", timestamp= datetime.datetime.utcnow() - datetime.timedelta(minutes=60))
                db.session.add(attempt)
                db.session.commit()
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)