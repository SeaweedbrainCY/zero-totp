from app import app
from database.db import db 
import unittest
import controllers
from unittest.mock import patch
from zero_totp_db_model.model import User, TOTP_secret
from environment import conf
import datetime
from database.user_repo import User as UserRepo
from database.preferences_repo import Preferences as PreferencesRepo
from database.session_token_repo import SessionTokenRepo

class TestUpdateEmail(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.client = self.application.test_client()
        self.endpoint = "/api/v1/update/email"
        
        self.user_id =1
        self.user2_id = 2
        self.blocked_user_id = 3
        self.unverified_user_id = 4

        self.user_email = "user1@test.test"
        self.user2_email = "user2@test.test"


        self.user_repo = UserRepo()
        self.preferences_repo = PreferencesRepo()
        self.session_token_repo = SessionTokenRepo()
        with self.application.app.app_context():
            db.create_all()
            self.user_repo.create(username="user1", email=self.user_email, password="password", randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now())
            self.user_repo.create(username="user2", email=self.user2_email, password="password", randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now())
            self.user_repo.create(username="user3", email="user3@test.test", password="password", randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now(), isBlocked=True)
            self.user_repo.create(username="user4", email="user4@test.test", password="password", randomSalt="salt",passphraseSalt="salt", isVerified=False, today=datetime.datetime.now())
            
            self.preferences_repo.create_default_preferences(user_id=1)

            _, self.session_token_user = self.session_token_repo.generate_session_token(self.user_id)
            _, self.session_token_user_blocked = self.session_token_repo.generate_session_token(self.blocked_user_id)
            _, self.session_token_user_unverified = self.session_token_repo.generate_session_token(self.unverified_user_id)
        

        self.send_verification_email = patch("controllers.send_verification_email").start()
        self.send_verification_email.return_value = True

        self.send_information_email = patch("Utils.utils.send_information_email").start()
        self.send_information_email.return_value = True


        self.check_email = patch("Utils.utils.check_email").start()
        self.check_email.return_value = True

        self.payload = {"email" : "test@test.com"}


    def tearDown(self):
        patch.stopall()
        with self.application.app.app_context():
            db.session.remove()
            db.drop_all()
    
    
    def test_update_email(self):
        with self.application.app.app_context():
            self.client.cookies = {"session-token": self.session_token_user}
            response = self.client.put(self.endpoint, json=self.payload)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(db.session.query(User).filter(User.id == self.user_id).first().mail , self.payload["email"])
            self.assertEqual(response.json()["message"], self.payload["email"])



    
    def test_update_email_bad_format(self):
        with self.application.app.app_context():
            self.client.cookies = {"session-token": self.session_token_user}
            self.check_email.return_value = False
            response = self.client.put(self.endpoint, json=self.payload)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(db.session.query(User).filter(User.id == self.user_id).first().mail , self.user_email)
    
    def test_update_email_already_used(self):
        with self.application.app.app_context():
            self.client.cookies = {"session-token": self.session_token_user}
            response = self.client.put(self.endpoint, json={"email": self.user2_email})
            self.assertEqual(response.status_code, 403)
    
    def test_update_email_with_own_email(self):
            with self.application.app.app_context():
                self.client.cookies = {"session-token": self.session_token_user}
                response = self.client.put(self.endpoint, json={"email": self.user_email})
                self.assertEqual(response.status_code, 201)
                self.assertEqual(response.json()["message"], self.user_email)
    

    
    def test_update_email_unverified(self):
        with self.application.app.app_context():
            self.client.cookies = {"session-token": self.session_token_user_unverified}
            response = self.client.put(self.endpoint, json=self.payload)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json()["message"], self.payload["email"])
            self.assertEqual(db.session.query(User).filter(User.id == self.unverified_user_id).first().mail , self.payload["email"])
    
    def test_update_email_blocked(self):
        with self.application.app.app_context():
            self.client.cookies = {"session-token": self.session_token_user_blocked}
            response = self.client.put(self.endpoint, json=self.payload)
            self.assertEqual(response.status_code, 403)
            self.assertNotEqual(db.session.query(User).filter(User.id == self.blocked_user_id).first().mail , self.payload["email"])
    
    def test_update_email_error_send_email(self):
        with self.application.app.app_context():
            self.client.cookies = {"session-token": self.session_token_user}
            self.send_verification_email.side_effect = Exception()
            response = self.client.put(self.endpoint, json=self.payload)
            self.assertEqual(response.status_code, 201)


    
