import unittest
from app import app
from database.db import db 
from environment import conf
from zero_totp_db_model.model import User as UserModel, RateLimiting
from unittest.mock import patch
import datetime
from database.session_token_repo import SessionTokenRepo


class TestSendVerificationController(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/email/send_verification"
        self.user_id = 1
        user = UserModel(id=self.user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role="admin")

        self.generate_new_email_verification_token = patch("Utils.utils.generate_new_email_verification_token", return_value="token").start()
        
        self.send_verification_email = patch("Email.send.send_verification_email", return_value=True).start()
        
        self.session_token_repo = SessionTokenRepo()

        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(user)
            _, self.session_token = self.session_token_repo.generate_session_token(user.id)
            db.session.commit()
    
       
    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()

    def test_send_verification_email(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.generate_new_email_verification_token.assert_called_once_with(user_id=self.user_id)
            self.send_verification_email.assert_called_once_with("user@user.com", "token")
    
    def test_send_verification_send_throw_error(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            self.send_verification_email.side_effect = Exception("Error while sending email")
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 500)
    
    def test_send_verification_rate_limited(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            for _ in range(conf.features.rate_limiting.send_email_attempts_limit_per_user):
                response = self.client.get(self.endpoint)
                self.assertEqual(response.status_code, 200)
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 429)
    
    def test_rate_limiting_expired(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            for _ in range(conf.features.rate_limiting.send_email_attempts_limit_per_user):
                attempt = RateLimiting(ip=None, user_id=self.user_id, action_type="send_verification_email", timestamp= datetime.datetime.utcnow() - datetime.timedelta(minutes=conf.features.rate_limiting.email_ban_time + 1))
                db.session.add(attempt)
                db.session.commit()
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)