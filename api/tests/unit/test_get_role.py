import unittest
from app import app
from database.db import db 
from environment import conf
from zero_totp_db_model.model import User as UserModel
from unittest.mock import patch
from CryptoClasses.jwt_func import generate_jwt, ISSUER as jwt_ISSUER, ALG as jwt_ALG
import datetime
import jwt


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

        admin_user = UserModel(id=self.admin_user_id,username="admin", mail="admin@admin.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role="admin")
        not_admin_user = UserModel(id=self.not_admin_user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role="user")
        user_without_role = UserModel(id=self.user_without_role_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role=None)
        user_blocked = UserModel(id=self.user_blocked_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role=None, isBlocked=True)
        user_unverified = UserModel(id=self.user_unverified_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = False, passphraseSalt = "AAAA", createdAt="01/01/2001", role=None, isBlocked=False)

        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(admin_user)
            db.session.add(not_admin_user)
            db.session.add(user_without_role)
            db.session.add(user_blocked)
            db.session.add(user_unverified)
            db.session.commit()
    
       
    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()
    
    def generate_expired_cookie(self, user_id):
        payload = {
            "iss": jwt_ISSUER,
            "sub": user_id,
            "iat": datetime.datetime.utcnow(),
            "nbf": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() - datetime.timedelta(hours=1),
        }
        jwt_cookie = jwt.encode(payload, conf.api.jwt_secret, algorithm=jwt_ALG)
        return jwt_cookie

    def test_get_role_admin(self):
        with self.flask_application.app.app_context():
            response = self.client.get(self.roleEndpoint, cookies={"api-key":generate_jwt(self.admin_user_id)})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["role"], "admin")

    def test_get_role_not_admin(self):
        with self.flask_application.app.app_context():
            self.client.cookies= { "api-key":generate_jwt(self.not_admin_user_id)}
            response = self.client.get(self.roleEndpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["role"], "user")
    
    def test_get_role_user_without_role(self):
         with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.user_without_role_id)}
            response = self.client.get(self.roleEndpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["role"], "user")
    
    def test_get_role_no_cookie(self):
        response = self.client.get(self.roleEndpoint)
        self.assertEqual(response.status_code, 401)
    
    def test_get_role_expired_cookie(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key":self.generate_expired_cookie(self.user_without_role_id)}
            response = self.client.get(self.roleEndpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_user_not_found(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(-1)}
            response = self.client.get(self.roleEndpoint)
            self.assertEqual(response.status_code, 401)
    
    def test_get_role_blocked_user(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.user_blocked_id)}
            response = self.client.get(self.roleEndpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_get_role_unverified_user(self):
        with self.flask_application.app.app_context():
            self.client.cookies= {"api-key" :generate_jwt(self.user_unverified_id)}
            response = self.client.get(self.roleEndpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["role"], "not_verified")

    

       


    