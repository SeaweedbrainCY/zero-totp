import unittest
from app import app
from database.db import db 
from environment import conf
from zero_totp_db_model.model import User as UserModel
from database.refresh_token_repo import RefreshTokenRepo
from database.rate_limiting_repo import RateLimitingRepo
from unittest.mock import patch
from CryptoClasses.jwt_func import generate_jwt, ISSUER, ALG, verify_jwt
import datetime
import jwt
from uuid import uuid4
from hashlib import sha256
from environment import logging


class TestRefreshAuthToken(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/auth/refresh"
        self.user_id = 1
        self.jwt_token = generate_jwt(self.user_id)
        with self.flask_application.app.app_context():
            user = UserModel(id=self.user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = False, passphraseSalt = "AAAA", createdAt="01/01/2001")
            db.create_all()
            db.session.add(user)
            db.session.commit()
        self.jti = verify_jwt(self.jwt_token)["jti"]
        self.refresh_token = str(uuid4())
        self.hashed_refresh_token = sha256(self.refresh_token.encode('utf-8')).hexdigest()
 
       
    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()
    
    def generate_jwt_expired(self, user_id):
        try:
            payload = {
                "iss": ISSUER,
                "sub": user_id,
                "iat": datetime.datetime.now(datetime.UTC),
                "nbf": datetime.datetime.now(datetime.UTC),
                "exp": datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=conf.api.session_token_validity),
                "jti": str(uuid4())
            }
            return jwt.encode(payload, conf.api.jwt_secret, algorithm=ALG)
        except Exception as e:
            logging.warning("Error while generating JWT : " + str(e))
            raise e
    
    def generate_self_signed_jwt(self,user_id):
        try:
            payload = {
                "iss": ISSUER,
                "sub": user_id,
                "iat": datetime.datetime.now(datetime.UTC),
                "nbf": datetime.datetime.now(datetime.UTC),
                "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=conf.api.session_token_validity),
                "jti": str(uuid4())
            }
            return jwt.encode(payload, str(uuid4()), algorithm=ALG)
        except Exception as e:
            logging.warning("Error while generating JWT : " + str(e))
            raise e


    
    def test_refresh_token(self):
        with self.flask_application.app.app_context():
            RefreshTokenRepo().create_refresh_token(self.user_id, self.jti,self.hashed_refresh_token)
            self.client.cookies = {"api-key": self.jwt_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Set-Cookie", response.headers)
            self.assertIn("api-key", response.headers["Set-Cookie"])
            self.assertIn("refresh-token", response.headers["Set-Cookie"])
            cookies = response.headers["Set-Cookie"].split("api-key=")
            self.assertEqual(len(cookies), 2, "api-key found multiple times in the response")
            if "refresh-token" in cookies[1]:
                cookies = cookies[1].split("refresh-token=")
                api_key_cookie = cookies[0]
                refresh_token_cookie = cookies[1]
            else:
                refresh_token_cookie = cookies[0]
                api_key_cookie = cookies[1]
            

            jwt_token = api_key_cookie.split(";")[0]
            self.assertIn("HttpOnly", api_key_cookie)
            self.assertIn("Secure", api_key_cookie)
            self.assertIn("SameSite=Lax", api_key_cookie)
            self.assertIn("Expires", api_key_cookie)
            self.assertIn("Path=/api/", api_key_cookie)
            
            self.assertIn("HttpOnly", refresh_token_cookie)
            self.assertIn("Secure", refresh_token_cookie)
            self.assertIn("SameSite=Lax", refresh_token_cookie)
            self.assertIn("Expires", refresh_token_cookie)
            self.assertIn("Path=/api/v1/auth/refresh", refresh_token_cookie)

            old_refresh_token = RefreshTokenRepo().get_refresh_token_by_hash(self.hashed_refresh_token)
            new_hashed_refresh_token = sha256(refresh_token_cookie.split(";")[0].encode('utf-8')).hexdigest()
            new_refresh_token = RefreshTokenRepo().get_refresh_token_by_hash(new_hashed_refresh_token)
            self.assertIsNotNone(old_refresh_token.revoke_timestamp)
            new_jti = verify_jwt(jwt_token, verify_exp=False)["jti"]
            self.assertIsNotNone(new_refresh_token)
            self.assertEqual(new_refresh_token.user_id, self.user_id)
            self.assertEqual(new_refresh_token.jti, new_jti)
            self.assertEqual(new_refresh_token.expiration, old_refresh_token.expiration)
            

    def test_refresh_token_with_expired_JWT(self):
        with self.flask_application.app.app_context():
            jwt_token = self.generate_jwt_expired(self.user_id)
            jti = verify_jwt(jwt_token, verify_exp=False)["jti"]
            RefreshTokenRepo().create_refresh_token(self.user_id, jti,self.hashed_refresh_token)
            self.client.cookies = {"api-key": jwt_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Set-Cookie", response.headers)
            self.assertIn("api-key", response.headers["Set-Cookie"])
            self.assertIn("refresh-token", response.headers["Set-Cookie"])
            cookies = response.headers["Set-Cookie"].split("api-key=")
            self.assertEqual(len(cookies), 2, "api-key found multiple times in the response")
            if "refresh-token" in cookies[1]:
                cookies = cookies[1].split("refresh-token=")
                api_key_cookie = cookies[0]
                refresh_token_cookie = cookies[1]
            else:
                refresh_token_cookie = cookies[0]
                api_key_cookie = cookies[1]
            

            jwt_token = api_key_cookie.split(";")[0]
            self.assertIn("HttpOnly", api_key_cookie)
            self.assertIn("Secure", api_key_cookie)
            self.assertIn("SameSite=Lax", api_key_cookie)
            self.assertIn("Expires", api_key_cookie)
            self.assertIn("Path=/api/", api_key_cookie)
            
            self.assertIn("HttpOnly", refresh_token_cookie)
            self.assertIn("Secure", refresh_token_cookie)
            self.assertIn("SameSite=Lax", refresh_token_cookie)
            self.assertIn("Expires", refresh_token_cookie)
            self.assertIn("Path=/api/v1/auth/refresh", refresh_token_cookie)

            old_refresh_token = RefreshTokenRepo().get_refresh_token_by_hash(self.hashed_refresh_token)
            new_hashed_refresh_token = sha256(refresh_token_cookie.split(";")[0].encode('utf-8')).hexdigest()
            new_refresh_token = RefreshTokenRepo().get_refresh_token_by_hash(new_hashed_refresh_token)
            self.assertIsNotNone(old_refresh_token.revoke_timestamp)
            new_jti = verify_jwt(jwt_token, verify_exp=False)["jti"]
            self.assertIsNotNone(new_refresh_token)
            self.assertEqual(new_refresh_token.user_id, self.user_id)
            self.assertEqual(new_refresh_token.jti, new_jti)
            self.assertEqual(new_refresh_token.expiration, old_refresh_token.expiration)
    
    def test_refresh_token_with_invalid_jti_same_user(self):
         with self.flask_application.app.app_context():
            jwt_token = self.generate_jwt_expired(self.user_id)
            jti = verify_jwt(jwt_token, verify_exp=False)["jti"]
            RefreshTokenRepo().create_refresh_token(self.user_id, jti,self.hashed_refresh_token)
            self.client.cookies = {"api-key": self.jwt_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertIsNotNone(RefreshTokenRepo().get_refresh_token_by_hash(self.hashed_refresh_token).revoke_timestamp)
    
    def  test_refresh_token_with_invalid_jti_other_user(self):
         with self.flask_application.app.app_context():
            user2 = UserModel(id=2,username="user2", mail="user2@mail.com", password="pass", derivedKeySalt="AA", isVerified = False, passphraseSalt = "AAA", createdAt="01/01/2001")
            jwt_token = generate_jwt(user2.id)
            RefreshTokenRepo().create_refresh_token(self.user_id, self.jti,self.hashed_refresh_token)
            self.client.cookies = {"api-key":jwt_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertIsNotNone(RefreshTokenRepo().get_refresh_token_by_hash(self.hashed_refresh_token).revoke_timestamp)
    
    def test_refresh_token_with_expired_refresh_token(self):
        with self.flask_application.app.app_context():
            RefreshTokenRepo().create_refresh_token(self.user_id, self.jti,self.hashed_refresh_token, expiration=datetime.datetime.now(datetime.UTC).timestamp())
            self.client.cookies = {"api-key": self.jwt_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_refresh_token_with_revoked_refresh_token(self):
        with self.flask_application.app.app_context():
            RefreshTokenRepo().create_refresh_token(self.user_id, self.jti,self.hashed_refresh_token)
            rt = RefreshTokenRepo().get_refresh_token_by_hash(self.hashed_refresh_token)
            rt.revoke_timestamp = datetime.datetime.now(datetime.UTC).timestamp()
            db.session.commit()
            self.client.cookies = {"api-key": self.jwt_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_refresh_token_with_unknown_refresh_token(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key": self.jwt_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_refresh_token_with_no_refresh_token(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key": self.jwt_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 401)
    
    def test_refresh_token_with_no_jwt_token(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 401)
    
    def test_refresh_token_with_no_cookies(self):
        with self.flask_application.app.app_context():
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 401)
    
    def test_refresh_token_with_invalid_jwt_token(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key": "invalid", "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_refresh_token_with_invalid_refresh_token_cookie(self):
        with self.flask_application.app.app_context():
            RefreshTokenRepo().create_refresh_token(self.user_id, self.jti,self.hashed_refresh_token, expiration=datetime.datetime.now(datetime.UTC).timestamp())
            self.client.cookies = {"api-key": self.jwt_token, "refresh-token": "invalid"}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_refresh_token_with_self_signed_JWT(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key": self.generate_self_signed_jwt(self.user_id), "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_refresh_roken_rate_limited(self):
        get_ip = patch("Utils.utils.get_ip").start()
        get_ip.return_value = "1.1.1.1"
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key": self.generate_self_signed_jwt(self.user_id), "refresh-token": self.refresh_token}
            for _ in range(conf.features.rate_limiting.login_attempts_limit_per_ip):    
                
                response = self.client.put(self.endpoint)
                self.assertEqual(response.status_code, 403)

            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 429)
            self.assertTrue(RateLimitingRepo().is_login_rate_limited("1.1.1.1"))
            

    


    
    

