import unittest
from app import app
from database.db import db
from unittest.mock import patch
from zero_totp_db_model.model import User, TOTP_secret, SessionToken, RefreshToken
from environment import conf
import datetime
from uuid import uuid4

class TestAllSecret(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/all_secrets"
        self.user_id = 1
        self.session_token = str(uuid4())
        self.secret1_id = str(uuid4())
        self.secret2_id = str(uuid4())
        with self.flask_application.app.app_context():
            user = User(id=self.user_id, isBlocked=False, isVerified=True, mail="mail", password="password",  role="user", username="username", createdAt="01/01/2001", derivedKeySalt="salt", passphraseSalt="salt")
            totp_secret = TOTP_secret(uuid=self.secret1_id, user_id=1, secret_enc = "enc_secret")
            totp_secret2 = TOTP_secret(uuid=self.secret2_id, user_id=1, secret_enc = "enc_secret2")
            session = SessionToken(id=str(uuid4()), token=self.session_token, user_id=self.user_id, expiration=(datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp())
            db.create_all()
            db.session.add(user)
            db.session.add(totp_secret)
            db.session.add(totp_secret2)
            db.session.add(session)
            db.session.commit()


    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()
 

    def test_get_all_secret(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            uuids = []
            for secret in response.json()["enc_secrets"]:
                uuids.append(secret["uuid"])
            self.assertIn(self.secret1_id, uuids)
            self.assertIn(self.secret2_id, uuids)
    
    def test_get_all_secret_no_cookie(self):
        with self.flask_application.app.app_context():
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 401)
    
    def test_get_all_secret_bad_cookie(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": str(uuid4())}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 401)
    
    def test_get_all_secret_expired_jwt(self):
        with self.flask_application.app.app_context():
            db.session.query(SessionToken).filter(SessionToken.token == self.session_token).update({"expiration": (datetime.datetime.now() - datetime.timedelta(hours=1)).timestamp()})
            db.session.commit()
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 401)
    
    def test_get_all_secret_no_secret(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            db.session.query(TOTP_secret).filter(TOTP_secret.user_id == self.user_id).delete()
            db.session.commit()
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 404)

    
    def test_get_all_secret_blocked_user(self):
         with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            db.session.query(User).filter(User.id == self.user_id).update({"isBlocked": True})
            db.session.commit()
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "User is blocked")
    
    def test_get_all_secret_unverified_user(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            db.session.query(User).filter(User.id == self.user_id).update({"isVerified": False})
            db.session.commit()
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "Not verified")