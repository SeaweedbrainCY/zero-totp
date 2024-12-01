from app import app
import unittest
from database.db import db
import controllers
from unittest.mock import patch
from zero_totp_db_model.model import ZKE_encryption_key, User
from environment import conf
from database.session_token_repo import SessionTokenRepo
from database.user_repo import User as UserRepo
from database.zke_repo import ZKE as ZKERepo
import datetime


class TestZKEEncryptedKey(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.client = self.application.test_client()
        self.endpoint = "/api/v1/zke_encrypted_key"

        self.user_id =1
        self.blocked_user_id = 2
        self.unverified_user_id = 3

        self.user_zke = "user1_zke"
        self.blocked_user_zke = "user2_zke"
        self.unverified_user_zke =  "user3_zke"

        self.user_repo = UserRepo()
        self.session_token_repo = SessionTokenRepo()
        self.zke_repo = ZKERepo()


        with self.application.app.app_context():
            db.create_all()
            db.session.commit()
            self.user_repo.create(username="user1", email="user1@test.test", password="password", randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now())
            self.user_repo.create(username="user3", email="user3@test.test", password="password", randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now(), isBlocked=True)
            self.user_repo.create(username="user4", email="user4@test.test", password="password", randomSalt="salt",passphraseSalt="salt", isVerified=False, today=datetime.datetime.now())

            self.zke_repo.create(user_id=self.user_id, encrypted_key=self.user_zke)
            self.zke_repo.create(user_id=self.blocked_user_id, encrypted_key=self.blocked_user_zke)
            self.zke_repo.create(user_id=self.unverified_user_id, encrypted_key=self.unverified_user_zke)

            _, self.session_token_user = self.session_token_repo.generate_session_token(self.user_id)
            _, self.session_token_user_blocked = self.session_token_repo.generate_session_token(self.blocked_user_id)
            _, self.session_token_user_unverified = self.session_token_repo.generate_session_token(self.unverified_user_id)
            
        


       



    def tearDown(self):
        patch.stopall()
        with self.application.app.app_context():
            db.session.remove()
            db.drop_all()
    
    
    def test_get_ZKE_encrypted_key(self):
        with self.application.app.app_context():
            self.client.cookies = {"session-token": self.session_token_user}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertIn(self.user_zke, response.json()['zke_encrypted_key'])

    def test_get_ZKE_blocked_user(self):
        with self.application.app.app_context():
            self.client.cookies = {"session-token": self.session_token_user_blocked}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_get_ZKE_unverified_user(self):
        with self.application.app.app_context():
            self.client.cookies = {"session-token": self.session_token_user_blocked}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)