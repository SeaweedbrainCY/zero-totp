import unittest
from app import app
from database.db import db
from environment import conf
from controllers import flask
from unittest.mock import patch
from uuid import uuid4
from database.user_repo import User as UserRepo
from database.session_token_repo import SessionTokenRepo
import datetime


class TestGetAuthFlow(unittest.TestCase):
    
        def setUp(self):
            if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
            self.application = app
            self.client = self.application.test_client()
            self.endpoint = "/api/v1/google-drive/oauth/authorization-flow"
            
            self.user_repo = UserRepo()
            self.session_repo = SessionTokenRepo()

            self.get_authorization_url_patch = patch("Oauth.oauth_flow.get_authorization_url").start()
            self.get_authorization_url_patch.return_value = "https://www.google.com", "state"
            with self.application.app.app_context():
                db.create_all()
                user = self.user_repo.create(username='user1', email='user1@test.com', password='test', randomSalt='salt', passphraseSalt='salt', today=datetime.datetime.now(), isVerified=True)
                _, self.session_token = self.session_repo.generate_session_token(user.id)
                db.session.commit()
        
        
        def test_get_auth_flow(self):
            with self.application.app.app_context():
                self.client.cookies = {"session-token": self.session_token}
                response = self.client.get(self.endpoint)
                self.assertEqual(response.status_code, 200)