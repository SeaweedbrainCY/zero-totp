import unittest
from app import app
from database.db import db
from environment import conf
from unittest.mock import patch
import datetime
from zero_totp_db_model.model import User as UserModel
from database.session_token_repo import SessionTokenRepo
from Utils import utils


class TestGetWhoami(unittest.TestCase):

    def setUp(self) -> None:
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/whoami"
        self.user_id = 1
        self.email = "user@test.com"
        self.username = "user"

        self.user_not_verified_id = 2
        self.user_not_verified_email = "user2@test.com"
        self.user_not_verified_username = "user2"

        self.session_repo = SessionTokenRepo()

        user1 = UserModel(id=self.user_id,username=self.username, mail=self.email, password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001")
        user2 = UserModel(id=self.user_not_verified_id,username=self.user_not_verified_email, mail=self.user_not_verified_username, password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001")
        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()

            self.session_token, _ = utils.generate_new_session(user=user1, ip_address=None)
            self.user_not_verified_session_token, _ = utils.generate_new_session(user=user2, ip_address=None)

    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()


    def test_get_whoami(self):
        with self.flask_application.app.app_context():
            self.client.cookies = { "session-token": self.session_token}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"username": self.username, "email": self.email, "id": self.user_id, "isEmailVerified": True})


    def test_get_whoami_not_verified_user(self):
        with self.flask_application.app.app_context():
            self.client.cookies = { "session-token": self.user_not_verified_session_token}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"username": self.username, "email": self.email, "id": self.user_id, "isEmailVerified": False})

    def test_get_whoami_not_verified_user_but_verification_not_enforced(self):
        with self.flask_application.app.app_context():
            conf.features.emails.require_email_validation = False
            self.client.cookies = { "session-token": self.user_not_verified_session_token}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"username": self.username, "email": self.email, "id": self.user_id, "isEmailVerified": True})
            conf.features.emails.require_email_validation = True

    def test_get_whoami_blocked_user(self):
        with self.flask_application.app.app_context():
            user = db.session.query(UserModel).filter_by(id=self.user_id).first()
            user.isBlocked = True
            db.session.commit()
            self.client.cookies = { "session-token": self.session_token}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json(), {"error": "User is blocked"})
