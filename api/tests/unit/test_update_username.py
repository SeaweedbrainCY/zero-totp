import unittest
from app import app
from database.db import db 
from environment import conf
from unittest.mock import patch
import datetime
from zero_totp_db_model.model import User as UserModel
from database.session_token_repo import SessionTokenRepo


class TestUpdateUsername(unittest.TestCase):

    def setUp(self) -> None:
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/update/username"
        self.user1_id = 1
        self.user2_id = 2
        self.blocked_user_id = 3
        self.unverified_user_id = 4

        
        user1 = UserModel(id=self.user1_id,username='user1', mail="user1@test.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001")
        user2 = UserModel(id=self.user2_id,username='user2', mail="user2@test.com",password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001")
        user_blocked = UserModel(id=self.blocked_user_id,username='user3', mail="user3@test.com",password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", isBlocked=True)
        unverified_user = UserModel(id=self.unverified_user_id,username='user4', mail="user4@test.com",password="pass", derivedKeySalt="AAA", isVerified = False, passphraseSalt = "AAAA", createdAt="01/01/2001")

        self.session_token_repo = SessionTokenRepo()

        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(user1)
            db.session.add(user2)
            db.session.add(user_blocked)
            db.session.add(unverified_user)
            db.session.commit()
            _, self.user1_session = self.session_token_repo.generate_session_token(self.user1_id)
            _, self.user2_session = self.session_token_repo.generate_session_token(self.user2_id)
            _, self.blocked_user_session = self.session_token_repo.generate_session_token(self.blocked_user_id)
            _, self.unverified_user_session = self.session_token_repo.generate_session_token(self.unverified_user_id)
            

    
    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()

    
    def test_update_username(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.user1_session}
            response = self.client.put(self.endpoint, json={"username": "new_username"})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(db.session.query(UserModel).filter_by(id=self.user1_id).first().username, "new_username")
    
    def test_update_username_already_taken(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.user1_session}
            response = self.client.put(self.endpoint, json={"username": "user2"})
            self.assertEqual(response.status_code, 409)
    
    def test_update_username_own_username(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.user1_session}
            response = self.client.put(self.endpoint, json={"username": "user1"})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(db.session.query(UserModel).filter_by(id=self.user1_id).first().username, "user1")
    

    
    def test_update_username_disabled_user(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.unverified_user_session}
            response = self.client.put(self.endpoint, json={"username": "new_username"})
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json(), {"error": "Not verified"})
    
    def test_update_username_blocked_user(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.blocked_user_session}
            response = self.client.put(self.endpoint, json={"username": "new_username"})
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json(), {"error": "User is blocked"})
     
    def test_update_username_too_long(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.user1_session}
            response = self.client.put(self.endpoint, json={"username": "a"*321})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {"message": "Username is too long"})
