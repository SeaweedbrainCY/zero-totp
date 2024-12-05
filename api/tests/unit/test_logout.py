import unittest
from app import app
from database.db import db 
from environment import conf
from zero_totp_db_model.model import User as UserModel
from database.refresh_token_repo import RefreshTokenRepo
from database.rate_limiting_repo import RateLimitingRepo
from database.session_token_repo import SessionTokenRepo
from unittest.mock import patch
import datetime
from uuid import uuid4
from hashlib import sha256
from environment import logging


class TestLogout(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/logout"
        self.user_id = 1
        with self.flask_application.app.app_context():
            user = UserModel(id=self.user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001")
            db.create_all()
            db.session.add(user)
            db.session.commit()
        self.refresh_token = str(uuid4())
        self.hashed_refresh_token = sha256(self.refresh_token.encode('utf-8')).hexdigest()
        
        with self.flask_application.app.app_context():
            self.session_id, self.session_token = SessionTokenRepo().generate_session_token(self.user_id)
            RefreshTokenRepo().create_refresh_token(self.user_id, self.session_id,self.hashed_refresh_token)
            
 
       
    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()
    
    
    def test_logout(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(SessionTokenRepo().get_session_token_by_id(self.session_id).revoke_timestamp)
            self.assertIsNotNone(RefreshTokenRepo().get_refresh_token_by_session_id(self.session_id).revoke_timestamp)

    
    def test_logout_no_session(self):
        with self.flask_application.app.app_context():
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 401)


