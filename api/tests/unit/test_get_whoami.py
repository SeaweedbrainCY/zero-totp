import unittest
from app import app
from database.db import db 
from environment import conf
from unittest.mock import patch
import datetime
from zero_totp_db_model.model import User as UserModel
from database.session_token_repo import SessionTokenRepo


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

        self.session_repo = SessionTokenRepo()
        
        user1 = UserModel(id=self.user_id,username=self.username, mail=self.email, password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001")
        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(user1)
            db.session.commit()

            _, self.session_token = self.session_repo.generate_session_token(self.user_id)
    
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
            self.assertEqual(response.json(), {"username": self.username, "email": self.email, "id": self.user_id})
    
    
    def test_get_whoami_not_verified_user(self):
        with self.flask_application.app.app_context():
            user = db.session.query(UserModel).filter_by(id=self.user_id).first()
            user.isVerified = False
            db.session.commit()
            self.client.cookies = { "session-token": self.session_token}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json(), {"error": "Not verified"})
    
    def test_get_whoami_blocked_user(self):
        with self.flask_application.app.app_context():
            user = db.session.query(UserModel).filter_by(id=self.user_id).first()
            user.isBlocked = True
            db.session.commit()
            self.client.cookies = { "session-token": self.session_token}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json(), {"error": "User is blocked"})
    