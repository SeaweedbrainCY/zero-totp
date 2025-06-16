import unittest
from app import app
from database.db import db
from database.user_repo import User as UserRepo
from environment import conf, logging
import datetime
from unittest.mock import patch



class TestGetDerivedKeySalt(unittest.TestCase):
    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.client = self.application.test_client()
        self.endpoint = "/api/v1/user/derived-key-salt"


        self.user_repo = UserRepo()

        with self.application.app.app_context():
            db.create_all()
            self.user_id = self.user_repo.create(username="user1", email="user1@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now()).id
            self.other_user_id = self.user_repo.create(username="user2", email="user2@mail.com", password="password",randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now()).id 
            
            _, self.session_token_user = self.session_token_repo.generate_session_token(self.user_id)
            _, self.session_token_other_user = self.session_token_repo.generate_session_token(self.other_user_id)
            db.session.commit()


    def tearDown(self):
        patch.stopall()
        with self.application.app.app_context():
            db.session.remove()
            db.drop_all()


    def test_get_derived_key_salt(self):
        with self.application.app.app_context():
            self.client.cookies = {"session-token": self.session_token_user}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertIn("derived_key_salt", response.json)
            self.assertEqual(response.json["derived_key_salt"], db.session.query(UserRepo).filter_by(id=self.user_id).first().derivedKeySalt)


