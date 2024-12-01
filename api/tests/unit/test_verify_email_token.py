import unittest
from app import app
from database.db import db 
from environment import conf
from zero_totp_db_model.model import User as UserModel, EmailVerificationToken as EmailVerificationToken_model, RateLimiting
from unittest.mock import patch
import datetime
from database.session_token_repo import SessionTokenRepo


class TestVerifyEmailToken(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/email/verify"
        self.user_id = 1
        self.already_verified_user_id = 2
        self.user_without_token_id = 3
        self.user_expired_token_id = 4
        self.user_wrong_token_id = 5
        self.blocked_user_id = 6

        user = UserModel(id=self.user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = False, passphraseSalt = "AAAA", createdAt="01/01/2001")
        user_already_verified = UserModel(id=self.already_verified_user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001")
        user_without_token = UserModel(id=self.user_without_token_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = False, passphraseSalt = "AAAA", createdAt="01/01/2001")
        user_expired_token = UserModel(id=self.user_expired_token_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = False, passphraseSalt = "AAAA", createdAt="01/01/2001")
        user_wrong_token = UserModel(id=self.user_wrong_token_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = False, passphraseSalt = "AAAA", createdAt="01/01/2001")
        blocked_user = UserModel(id=self.blocked_user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = False, passphraseSalt = "AAAA", createdAt="01/01/2001", isBlocked=True)
        


        token = EmailVerificationToken_model(user_id=self.user_id, token="token", expiration=(datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).timestamp())
        expired_token = EmailVerificationToken_model(user_id=self.user_expired_token_id, token="token", expiration=(datetime.datetime.utcnow() - datetime.timedelta(minutes=1)).timestamp())
        wrongToken = EmailVerificationToken_model(user_id=self.user_wrong_token_id, token="wrongToken", expiration=(datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).timestamp())

        self.session_token_repo = SessionTokenRepo()

       

        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(user)
            db.session.add(token)
            db.session.add(expired_token)
            db.session.add(user_already_verified)
            db.session.add(wrongToken)
            db.session.add(user_without_token)
            db.session.add(user_expired_token)
            db.session.add(user_wrong_token)
            db.session.add(blocked_user)
            db.session.commit()

            _, self.user_session = self.session_token_repo.generate_session_token(self.user_id)
            _, self.already_verified_user_session = self.session_token_repo.generate_session_token(self.already_verified_user_id)
            _, self.user_without_token_session = self.session_token_repo.generate_session_token(self.user_without_token_id)
            _, self.user_expired_token_session = self.session_token_repo.generate_session_token(self.user_expired_token_id)
            _, self.user_wrong_token_session = self.session_token_repo.generate_session_token(self.user_wrong_token_id)
            _, self.blocked_user_session = self.session_token_repo.generate_session_token(self.blocked_user_id)

    
       
    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()

    
    def test_verify_token(self):
        with self.flask_application.app.app_context():
            body = {"token": "token"}
            self.client.cookies = {"session-token": self.user_session}
            response = self.client.put(self.endpoint, json=body)
            self.assertEqual(response.status_code, 200)
            user = UserModel.query.filter_by(id=self.user_id).first()
            self.assertTrue(user.isVerified)
            token = EmailVerificationToken_model.query.filter_by(user_id=self.user_id).first()
            self.assertIsNone(token)

    def test_verify_already_verified(self):
         with self.flask_application.app.app_context():
            body = {"token": "anythin"}
            self.client.cookies = {"session-token": self.already_verified_user_session}
            response = self.client.put(self.endpoint, json=body)
            self.assertEqual(response.status_code, 200)
            user = UserModel.query.filter_by(id=self.already_verified_user_id).first()
            self.assertTrue(user.isVerified)
            token = EmailVerificationToken_model.query.filter_by(user_id=self.already_verified_user_id).first()
            self.assertIsNone(token)
    
    def test_verify_expired_token(self):
        with self.flask_application.app.app_context():
            body = {"token": "token"}
            self.client.cookies = {"session-token": self.user_expired_token_session}
            response = self.client.put(self.endpoint, json=body)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["message"], "email_verif.error.expired")
            user = UserModel.query.filter_by(id=self.user_expired_token_id).first()
            self.assertFalse(user.isVerified)
            token = EmailVerificationToken_model.query.filter_by(user_id=self.user_expired_token_id).first()
            self.assertIsNone(token)
    
    def test_verify_wrong_token(self):
        with self.flask_application.app.app_context():
            body = {"token": "token"}
            self.client.cookies = {"session-token": self.user_wrong_token_session}
            response = self.client.put(self.endpoint, json=body)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["message"],  "email_verif.error.failed")
            self.assertEqual(response.json()["attempt_left"], 4)
            user = UserModel.query.filter_by(id=self.user_wrong_token_id).first()
            self.assertFalse(user.isVerified)
            token = EmailVerificationToken_model.query.filter_by(user_id=self.user_wrong_token_id).first()
            self.assertIsNotNone(token)
    
    def test_verify_no_token(self):
        with self.flask_application.app.app_context():
            body = {"token": "token"}
            self.client.cookies = {"session-token": self.user_without_token_session}
            response = self.client.put(self.endpoint, json=body)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["message"], "email_verif.error.no_active_code")
            user = UserModel.query.filter_by(id=self.user_without_token_id).first()
            self.assertFalse(user.isVerified)
    
    def test_verify_after_5_wrong_attempts(self):
        with self.flask_application.app.app_context():
            body = {"token": "token"}
            self.client.cookies = {"session-token": self.user_wrong_token_session}
            for i in range(5):
                response = self.client.put(self.endpoint, json=body)
                self.assertEqual(response.status_code, 403)
                self.assertEqual(response.json()["message"],  "email_verif.error.failed")
                self.assertEqual(response.json()["attempt_left"], 4-i)
            response = self.client.put(self.endpoint, json=body)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["message"],"email_verif.error.too_many_failed")

    
    def test_flush_rate_limiting_table(self):
        with self.flask_application.app.app_context():
            for _ in range(conf.features.rate_limiting.send_email_attempts_limit_per_user):
                attempt = RateLimiting(ip=None, user_id=self.user_id, action_type="send_verification_email", timestamp= datetime.datetime.utcnow() - datetime.timedelta(minutes=60))
                db.session.add(attempt)
                db.session.commit()
            body = {"token": "token"}
            self.client.cookies = {"session-token": self.user_session}
            response = self.client.put(self.endpoint, json=body)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(RateLimiting.query.all()), 0)
    
    def test_verify_blocked_user(self):
        with self.flask_application.app.app_context():
            body = {"token": "token"}
            self.client.cookies = {"session-token": self.blocked_user_session}
            response = self.client.put(self.endpoint, json=body)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "User is blocked")
            user = UserModel.query.filter_by(id=self.blocked_user_id).first()
            self.assertFalse(user.isVerified)


