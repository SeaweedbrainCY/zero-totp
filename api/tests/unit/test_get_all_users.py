import unittest
from app import app
from database.db import db 
from environment import conf
from zero_totp_db_model.model import User as UserModel, Admin as AdminModel
from unittest.mock import patch
from CryptoClasses.jwt_func import generate_jwt, verify_jwt, ISSUER as jwt_ISSUER, ALG as jwt_ALG
import datetime
import jwt


class TestGetAllUsers(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.application = app
        self.client = self.application.test_client()
        self.getAllUsersEndpoint = "/api/v1/admin/users"
        self.admin_user_id = 1
        self.normal_user_id = 2

        admin_user = UserModel(id=self.admin_user_id,username="admin", mail="admin@admin.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role="admin")
        normal_user = UserModel(id=self.normal_user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role=None)
        admin_user_token = AdminModel(user_id=self.admin_user_id, token_hashed="token", token_expiration=(datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).timestamp())
        with self.application.app.app_context():
            db.create_all()
            db.session.add(admin_user)
            db.session.add(admin_user_token)
            db.session.add(normal_user)
            db.session.commit()
    
       
    def tearDown(self):
        with self.application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()
    
    def generate_expired_cookie(self, user_id, admin=False):
        payload = {
            "iss": jwt_ISSUER,
            "sub": user_id,
            "iat": datetime.datetime.utcnow(),
            "nbf": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() - datetime.timedelta(hours=1),
        }
        if admin:
            payload["admin"] = True
        jwt_cookie = jwt.encode(payload, conf.api.jwt_secret, algorithm=jwt_ALG)
        return jwt_cookie

    def test_get_all_users_success(self):
        with self.application.app.app_context():
           self.client.cookies = {"api-key":generate_jwt(self.admin_user_id),"admin-api-key":generate_jwt(self.admin_user_id, admin=True)}
           response = self.client.get(self.getAllUsersEndpoint)
           self.assertEqual(response.status_code, 200)
           self.assertIn("users", response.json())
           self.assertEqual(len(response.json()["users"]), 2)
    
    def test_get_all_users_no_admin_cookie_but_admin(self):
        with self.application.app.app_context():
           self.client.cookies = {"api-key":generate_jwt(self.admin_user_id)}
           response = self.client.get(self.getAllUsersEndpoint)
           self.assertEqual(response.status_code, 403)
    
    def test_get_all_users_no_admin(self):
        with self.application.app.app_context():
           self.client.cookies = {"api-key":generate_jwt(self.normal_user_id)}
           response = self.client.get(self.getAllUsersEndpoint)
           self.assertEqual(response.status_code, 403)
    
    def test_get_all_users_no_cookie(self):
        with self.application.app.app_context():
           response = self.client.get(self.getAllUsersEndpoint)
           self.assertEqual(response.status_code, 401)
    
    def test_get_all_users_expired_admin_cookie(self):
        with self.application.app.app_context():
           self.client.cookies = {"api-key":generate_jwt(self.admin_user_id), "admin-api-key":self.generate_expired_cookie(self.admin_user_id, admin=True)}

           response = self.client.get(self.getAllUsersEndpoint)
           self.assertEqual(response.status_code, 403)
    
    def test_get_all_users_expired_cookie(self):
        with self.application.app.app_context():
           self.client.cookies = {"api-key":self.generate_expired_cookie(self.admin_user_id), "admin-api-key":generate_jwt(self.admin_user_id, admin=True)}
           response = self.client.get(self.getAllUsersEndpoint)
           self.assertEqual(response.status_code, 403)
    
    def test_get_all_users_bad_admin_cookie(self):
        with self.application.app.app_context():
           self.client.cookies = {"api-key":generate_jwt(self.admin_user_id), "admin-api-key":"bad cookie"}
           response = self.client.get(self.getAllUsersEndpoint)
           self.assertEqual(response.status_code, 401)
    
    def test_get_all_users_user_admin_not_found(self):
         with self.application.app.app_context():
           self.client.cookies = {"api-key":generate_jwt(self.admin_user_id), "admin-api-key":generate_jwt(-1, admin=True)}
           response = self.client.get(self.getAllUsersEndpoint)
           self.assertEqual(response.status_code, 403) 

    def test_get_all_users_user_not_found(self):
         with self.application.app.app_context():
           self.client.cookies = {"api-key":generate_jwt(-1), "admin-api-key":generate_jwt(self.admin_user_id, admin=True)}
           response = self.client.get(self.getAllUsersEndpoint)
           self.assertEqual(response.status_code, 403) 
    
    def test_get_all_users_admin_cookie_but_user_role(self):
         with self.application.app.app_context():
           self.client.cookies = {"api-key":generate_jwt(self.normal_user_id), "admin-api-key":generate_jwt(self.normal_user_id, admin=True)}
           response = self.client.get(self.getAllUsersEndpoint)
           self.assertEqual(response.status_code, 403) 
    
    def test_get_all_users_no_admin_field_in_jwt(self):
         with self.application.app.app_context():
           self.client.cookies = {"api-key":generate_jwt(self.admin_user_id), "admin-api-key":generate_jwt(self.admin_user_id)}
           response = self.client.get(self.getAllUsersEndpoint)
           self.assertEqual(response.status_code, 403) 
           

       


    