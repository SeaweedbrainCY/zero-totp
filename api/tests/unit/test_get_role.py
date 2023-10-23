import unittest
from app import create_app
from database.db import db 
import environment as env
from database.model import User as UserModel
from unittest.mock import patch
from CryptoClasses.jwt_func import generate_jwt, ISSUER as jwt_ISSUER, ALG as jwt_ALG
import datetime
import jwt


class TestJWT(unittest.TestCase):

    def setUp(self):
        env.db_uri = "sqlite:///:memory:"
        self.app = create_app()
        self.client = self.app.test_client()
        self.roleEndpoint = "/role"
        self.admin_user_id = 1
        self.not_admin_user_id = 2
        self.user_without_role_id = 3

        admin_user = UserModel(id=self.admin_user_id,username="admin", mail="admin@admin.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role="admin")
        not_admin_user = UserModel(id=self.not_admin_user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role="user")
        user_without_role = UserModel(id=self.user_without_role_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role=None)
        with self.app.app_context():
            db.create_all()
            db.session.add(admin_user)
            db.session.add(not_admin_user)
            db.session.add(user_without_role)
            db.session.commit()
    
       
    def tearDown(self):
        with self.app.app_context():
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
        jwt_cookie = jwt.encode(payload, env.jwt_secret, algorithm=jwt_ALG)
        return jwt_cookie

    def test_get_role_admin(self):
        with self.app.app_context():
            self.client.set_cookie("localhost", "api-key",generate_jwt(self.admin_user_id))
            response = self.client.get(self.roleEndpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["role"], "admin")

    def test_get_role_not_admin(self):
        with self.app.app_context():
            self.client.set_cookie("localhost", "api-key",generate_jwt(self.not_admin_user_id))
            response = self.client.get(self.roleEndpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["role"], "user")
    
    def test_get_role_user_without_role(self):
         with self.app.app_context():
            self.client.set_cookie("localhost", "api-key",generate_jwt(self.user_without_role_id))
            response = self.client.get(self.roleEndpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["role"], "user")
    
    def test_get_role_no_cookie(self):
        response = self.client.get(self.roleEndpoint)
        self.assertEqual(response.status_code, 401)
    
    def test_get_role_expired_cookie(self):
        with self.app.app_context():
            self.client.set_cookie("localhost", "api-key",self.generate_expired_cookie(self.user_without_role_id))
            response = self.client.get(self.roleEndpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_user_not_found(self):
        with self.app.app_context():
            self.client.set_cookie("localhost", "api-key", generate_jwt(-1))
            response = self.client.get(self.roleEndpoint)
            self.assertEqual(response.status_code, 404)

    

       


    