import unittest
from main_api.app import app
from db_models.db import db 
from db_models.model import User as UserModel, Admin as AdminModel
from unittest.mock import patch
from main_api.CryptoClasses.jwt_func import generate_jwt, verify_jwt, ISSUER as jwt_ISSUER, ALG as jwt_ALG
import datetime
import jwt
from main_api.environment import conf


class TestJWT(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.client = self.application.test_client()
        self.loginEndpoint = "/admin/login"
        self.admin_user_id = 1
        self.admin_user_without_token_id = 2
        self.not_admin_user_id = 3
        self.admin_with_expired_token_id = 4

        admin_user = UserModel(id=self.admin_user_id,username="admin", mail="admin@admin.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role="admin")
        admin_user_without_token = UserModel(id=self.admin_user_without_token_id,username="admin", mail="admin@admin.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role="admin")
        admin_token = AdminModel(user_id=self.admin_user_id, token_hashed="token", token_expiration=(datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).timestamp())
        not_admin_user = UserModel(id=self.not_admin_user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role="user")
        admin_with_expired_token = UserModel(id=self.admin_with_expired_token_id,username="admin_with_expired_token", mail="admin@admin.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role="admin")
        admin_with_expired_token_token = AdminModel(user_id=self.admin_with_expired_token_id, token_hashed="token", token_expiration=(datetime.datetime.utcnow() - datetime.timedelta(minutes=1)).timestamp())
        with self.application.app.app_context():
            db.create_all()
            db.session.add(admin_user)
            db.session.add(admin_token)
            db.session.add(not_admin_user)
            db.session.add(admin_user_without_token)
            db.session.add(admin_with_expired_token)
            db.session.add(admin_with_expired_token_token)
            db.session.commit()
        
        self.checkpw = patch("CryptoClasses.hash_func.Bcrypt.checkpw").start()

       


        
    def tearDown(self):
        with self.application.app.app_context():
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
        jwtCookie = jwt.encode(payload, conf.api.jwt_secret, algorithm=jwt_ALG)
        return jwtCookie
    

    def test_admin_login_success(self):
        with self.application.app.app_context():
            self.checkpw.return_value = True
            self.client.cookies = {"api-key":generate_jwt(self.admin_user_id)}
            response = self.client.post(self.loginEndpoint, json={"token": "token"})
            self.assertEqual(response.status_code, 200)
            self.assertIn("admin-api-key", response.headers["Set-Cookie"])
            self.assertIn("HttpOnly", response.headers["Set-Cookie"])
            self.assertIn("Secure", response.headers["Set-Cookie"])
            self.assertIn("SameSite=Lax", response.headers["Set-Cookie"])
            self.assertIn("Expires", response.headers["Set-Cookie"])
            jwt_token = response.headers["Set-Cookie"].strip().split("admin-api-key=")[1].split(";")[0]
            self.assertTrue(verify_jwt(jwt_token))
            self.assertTrue(verify_jwt(jwt_token)["admin"])
    
    def test_admin_login_but_bad_token(self):
        with self.application.app.app_context():
            self.checkpw.return_value = False
            self.client.cookies = {"api-key":generate_jwt(self.admin_user_id)}
            response = self.client.post(self.loginEndpoint, json={"token": "token"})
            self.assertEqual(response.status_code, 403)

    
    def test_admin_login_but_no_token(self):
        with self.application.app.app_context():
            self.checkpw.return_value = True
            self.client.cookies = {"api-key":generate_jwt(self.admin_user_without_token_id)}
            response = self.client.post(self.loginEndpoint, json={"token": "token"})
            self.assertEqual(response.status_code, 403)
    
    def test_admin_login_but_no_admin_role(self):
        with self.application.app.app_context():
            self.checkpw.return_value = True
            self.client.cookies = {"api-key":generate_jwt(self.not_admin_user_id)}
            response = self.client.post(self.loginEndpoint, json={"token": "token"})
            self.assertEqual(response.status_code, 403)
    
    def test_admin_login_but_no_cookie(self):
        with self.application.app.app_context():
            response = self.client.post(self.loginEndpoint, json={"token": "token"})
            self.assertEqual(response.status_code, 401)
    
    def test_admin_login_but_expired_cookie(self):
         with self.application.app.app_context():
            self.checkpw.return_value = True
            self.client.cookies = {"api-key":self.generate_expired_cookie(self.admin_user_id)} 
            response = self.client.post(self.loginEndpoint, json={"token": "token"})
            self.assertEqual(response.status_code, 403)
    
    def test_admin_login_but_no_user(self):
        with self.application.app.app_context():
            self.checkpw.return_value = True
            self.client.cookies = {"api-key":generate_jwt(-1)} 
            response = self.client.post(self.loginEndpoint, json={"token": "token"})
            self.assertEqual(response.status_code, 403)
    
    def test_admin_with_expired_token(self):
        with self.application.app.app_context():
            self.checkpw.return_value = True
            self.client.cookies = {"api-key":generate_jwt(self.admin_with_expired_token_id)}
            response = self.client.post(self.loginEndpoint, json={"token": "token"})
            self.assertEqual(response.status_code, 403)