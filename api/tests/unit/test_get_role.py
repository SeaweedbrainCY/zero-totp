import unittest
from app import app
from database.db import db 
from environment import conf
from zero_totp_db_model.model import User as UserModel
from unittest.mock import patch
import datetime
from database.session_token_repo import SessionTokenRepo


class TestGetRole(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.roleEndpoint = "/api/v1/role"
        self.admin_user_id = 1
        self.not_admin_user_id = 2
        self.user_without_role_id = 3
        self.user_blocked_id = 4
        self.user_unverified_id = 5

        self.session_repo = SessionTokenRepo()

        admin_user = UserModel(id=self.admin_user_id,username="admin", mail="admin@admin.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role="admin")
        not_admin_user = UserModel(id=self.not_admin_user_id,username="user1", mail="user1@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role="user")
        user_without_role = UserModel(id=self.user_without_role_id,username="user2", mail="user2@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role=None)
        user_blocked = UserModel(id=self.user_blocked_id,username="user3", mail="user3@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role=None, isBlocked=True)
        user_unverified = UserModel(id=self.user_unverified_id,username="user4", mail="user4@user.com", password="pass", derivedKeySalt="AAA", isVerified = False, passphraseSalt = "AAAA", createdAt="01/01/2001", role=None, isBlocked=False)

        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(admin_user)
            db.session.add(not_admin_user)
            db.session.add(user_without_role)
            db.session.add(user_blocked)
            db.session.add(user_unverified)
            db.session.commit()

            _, self.session_token_admin = self.session_repo.generate_session_token(self.admin_user_id)
            _, self.session_token_not_admin = self.session_repo.generate_session_token(self.not_admin_user_id)
            _, self.session_token_user_without_role = self.session_repo.generate_session_token(self.user_without_role_id)
            _, self.session_token_user_blocked = self.session_repo.generate_session_token(self.user_blocked_id)
            _, self.session_token_user_unverified = self.session_repo.generate_session_token(self.user_unverified_id)

            
    
       
    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()
    
   

    def test_get_role_admin(self):
        with self.flask_application.app.app_context():
            response = self.client.get(self.roleEndpoint, cookies={"session-token": self.session_token_admin})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["role"], "admin")

    def test_get_role_not_admin(self):
        with self.flask_application.app.app_context():
            response = self.client.get(self.roleEndpoint, cookies= { "session-token": self.session_token_not_admin })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["role"], "user")
    
    def test_get_role_user_without_role(self):
         with self.flask_application.app.app_context():
            self.client.cookies= { "session-token": self.session_token_user_without_role}
            response = self.client.get(self.roleEndpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["role"], "user")
    
    def test_get_role_no_cookie(self):
        response = self.client.get(self.roleEndpoint)
        self.assertEqual(response.status_code, 401)

    
    def test_get_role_blocked_user(self):
        with self.flask_application.app.app_context():
            self.client.cookies= { "session-token": self.session_token_user_blocked}
            response = self.client.get(self.roleEndpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_get_role_unverified_user(self):
        with self.flask_application.app.app_context():
            self.client.cookies= { "session-token": self.session_token_user_unverified}
            response = self.client.get(self.roleEndpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["role"], "not_verified")

    

       


    