import unittest
from app import app
from database.db import db 
from environment import conf
from zero_totp_db_model.model import User as UserModel, SessionToken
from database.refresh_token_repo import RefreshTokenRepo
from database.rate_limiting_repo import RateLimitingRepo
from database.session_token_repo import SessionTokenRepo
from unittest.mock import patch
import datetime
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
        with self.flask_application.app.app_context():
            user = UserModel(id=self.user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = False, passphraseSalt = "AAAA", createdAt="01/01/2001")
            db.create_all()
            db.session.add(user)
            db.session.commit()
        self.refresh_token = str(uuid4())
        self.hashed_refresh_token = sha256(self.refresh_token.encode('utf-8')).hexdigest()
 
       
    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()


    
    def test_refresh_token(self):
        with self.flask_application.app.app_context():
            session_id, session_token = SessionTokenRepo().generate_session_token(self.user_id)
            RefreshTokenRepo().create_refresh_token(self.user_id, session_id,self.hashed_refresh_token)
            self.client.cookies = {"session-token": session_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Set-Cookie", response.headers)
            self.assertIn("session-token", response.headers["Set-Cookie"])
            self.assertIn("refresh-token", response.headers["Set-Cookie"])
            cookies = response.headers["Set-Cookie"].split("session-token=")
            self.assertEqual(len(cookies), 2, "ession-token found multiple times in the response")
            if "refresh-token" in cookies[1]:
                cookies = cookies[1].split("refresh-token=")
                session_token_cookie = cookies[0]
                refresh_token_cookie = cookies[1]
            else:
                refresh_token_cookie = cookies[0]
                session_token_cookie = cookies[1]
            

            self.assertIn("HttpOnly", session_token_cookie)
            self.assertIn("Secure", session_token_cookie)
            self.assertIn("SameSite=Lax", session_token_cookie)
            self.assertIn("Expires", session_token_cookie)
            self.assertIn("Path=/api/", session_token_cookie)
            
            self.assertIn("HttpOnly", refresh_token_cookie)
            self.assertIn("Secure", refresh_token_cookie)
            self.assertIn("SameSite=Lax", refresh_token_cookie)
            self.assertIn("Expires", refresh_token_cookie)
            self.assertIn("Path=/api/v1/auth/refresh", refresh_token_cookie)

            old_refresh_token = RefreshTokenRepo().get_refresh_token_by_hash(self.hashed_refresh_token)
            new_hashed_refresh_token = sha256(refresh_token_cookie.split(";")[0].encode('utf-8')).hexdigest()
            new_refresh_token = RefreshTokenRepo().get_refresh_token_by_hash(new_hashed_refresh_token)
            new_session_token = SessionTokenRepo().get_session_token_by_id(new_refresh_token.session_token_id)
            self.assertIn(new_session_token.token, session_token_cookie)
            self.assertIsNotNone(old_refresh_token.revoke_timestamp)
            self.assertIsNotNone(SessionTokenRepo().get_session_token(session_token).revoke_timestamp)
            self.assertIsNotNone(new_refresh_token)
            self.assertIsNone(new_refresh_token.revoke_timestamp)
            self.assertIsNotNone(new_session_token)
            self.assertIsNone(new_session_token.revoke_timestamp)
            self.assertEqual(new_refresh_token.user_id, self.user_id)
            self.assertEqual(new_session_token.user_id, self.user_id)
            self.assertEqual(new_refresh_token.expiration, old_refresh_token.expiration)
            

    def test_refresh_token_with_expired_session(self):
       with self.flask_application.app.app_context():
            session_id, session_token = SessionTokenRepo().generate_session_token(self.user_id)
            SessionToken.query.filter_by(id=session_id).first().expiration = datetime.datetime.now(datetime.UTC).timestamp()
            db.session.commit()
            RefreshTokenRepo().create_refresh_token(self.user_id, session_id,self.hashed_refresh_token)
            self.client.cookies = {"session-token": session_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Set-Cookie", response.headers)
            self.assertIn("session-token", response.headers["Set-Cookie"])
            self.assertIn("refresh-token", response.headers["Set-Cookie"])
            cookies = response.headers["Set-Cookie"].split("session-token=")
            self.assertEqual(len(cookies), 2, "ession-token found multiple times in the response")
            if "refresh-token" in cookies[1]:
                cookies = cookies[1].split("refresh-token=")
                session_token_cookie = cookies[0]
                refresh_token_cookie = cookies[1]
            else:
                refresh_token_cookie = cookies[0]
                session_token_cookie = cookies[1]
            

            self.assertIn("HttpOnly", session_token_cookie)
            self.assertIn("Secure", session_token_cookie)
            self.assertIn("SameSite=Lax", session_token_cookie)
            self.assertIn("Expires", session_token_cookie)
            self.assertIn("Path=/api/", session_token_cookie)
            
            self.assertIn("HttpOnly", refresh_token_cookie)
            self.assertIn("Secure", refresh_token_cookie)
            self.assertIn("SameSite=Lax", refresh_token_cookie)
            self.assertIn("Expires", refresh_token_cookie)
            self.assertIn("Path=/api/v1/auth/refresh", refresh_token_cookie)

            old_refresh_token = RefreshTokenRepo().get_refresh_token_by_hash(self.hashed_refresh_token)
            new_hashed_refresh_token = sha256(refresh_token_cookie.split(";")[0].encode('utf-8')).hexdigest()
            new_refresh_token = RefreshTokenRepo().get_refresh_token_by_hash(new_hashed_refresh_token)
            new_session_token = SessionTokenRepo().get_session_token_by_id(new_refresh_token.session_token_id)
            self.assertIn(new_session_token.token, session_token_cookie)
            self.assertIsNotNone(old_refresh_token.revoke_timestamp)
            self.assertIsNotNone(SessionTokenRepo().get_session_token(session_token).revoke_timestamp)
            self.assertIsNotNone(new_refresh_token)
            self.assertIsNone(new_refresh_token.revoke_timestamp)
            self.assertIsNotNone(new_session_token)
            self.assertIsNone(new_session_token.revoke_timestamp)
            self.assertEqual(new_refresh_token.user_id, self.user_id)
            self.assertEqual(new_session_token.user_id, self.user_id)
            self.assertEqual(new_refresh_token.expiration, old_refresh_token.expiration)
    
    def test_refresh_token_same_user_token_but_unpaired(self):
         with self.flask_application.app.app_context():
            session_id1, session_token1 = SessionTokenRepo().generate_session_token(self.user_id)
            session_id2, session_token2 = SessionTokenRepo().generate_session_token(self.user_id)

            refresh_token2 = str(uuid4())
            hashed_refresh_token2 = sha256(refresh_token2.encode('utf-8')).hexdigest()

            RefreshTokenRepo().create_refresh_token(self.user_id, session_id1,self.hashed_refresh_token)
            RefreshTokenRepo().create_refresh_token(self.user_id, session_id2,hashed_refresh_token2)


            self.client.cookies = {"session-token": session_token2, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertIsNotNone(RefreshTokenRepo().get_refresh_token_by_hash(self.hashed_refresh_token).revoke_timestamp)
            self.assertIsNotNone(SessionTokenRepo().get_session_token(session_token2).revoke_timestamp)
            self.assertIsNotNone(RefreshTokenRepo().get_refresh_token_by_hash(hashed_refresh_token2).revoke_timestamp)
            self.assertIsNotNone(SessionTokenRepo().get_session_token(session_token1).revoke_timestamp)

    
    def test_refresh_token_with_token_from_other_user(self):
         with self.flask_application.app.app_context():
            session_id1, session_token1 = SessionTokenRepo().generate_session_token(self.user_id)
            session_id2, session_token2 = SessionTokenRepo().generate_session_token(20)

            refresh_token2 = str(uuid4())
            hashed_refresh_token2 = sha256(refresh_token2.encode('utf-8')).hexdigest()

            RefreshTokenRepo().create_refresh_token(self.user_id, session_id1,self.hashed_refresh_token)
            RefreshTokenRepo().create_refresh_token(20, session_id2,hashed_refresh_token2)


            self.client.cookies = {"session-token": session_token2, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertIsNotNone(RefreshTokenRepo().get_refresh_token_by_hash(self.hashed_refresh_token).revoke_timestamp)
            self.assertIsNotNone(SessionTokenRepo().get_session_token(session_token2).revoke_timestamp)
            self.assertIsNotNone(RefreshTokenRepo().get_refresh_token_by_hash(hashed_refresh_token2).revoke_timestamp)
            self.assertIsNotNone(SessionTokenRepo().get_session_token(session_token1).revoke_timestamp)
    
    def test_refresh_token_with_expired_refresh_token(self):
        with self.flask_application.app.app_context():
            session_id, session_token = SessionTokenRepo().generate_session_token(self.user_id)
            rt = RefreshTokenRepo().create_refresh_token(self.user_id, session_id,self.hashed_refresh_token)
            rt.expiration = datetime.datetime.now(datetime.UTC).timestamp()
            db.session.commit()
            self.client.cookies = {"session-token":session_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_refresh_token_with_revoked_refresh_token(self):
        with self.flask_application.app.app_context():
            session_id, session_token = SessionTokenRepo().generate_session_token(self.user_id)
            rt = RefreshTokenRepo().create_refresh_token(self.user_id, session_id,self.hashed_refresh_token)
            RefreshTokenRepo().revoke(rt.id)
            self.client.cookies = {"session-token":session_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_refresh_token_with_unknown_refresh_token(self):
        with self.flask_application.app.app_context():
            _, session_token = SessionTokenRepo().generate_session_token(self.user_id)
            self.client.cookies = {"session-token": session_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_refresh_token_with_no_refresh_token(self):
        with self.flask_application.app.app_context():
            _, session_token = SessionTokenRepo().generate_session_token(self.user_id)
            self.client.cookies = {"session-token": session_token}
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
    
    def test_refresh_token_with_invalid_session_token(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": "session", "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 401)
    
    def test_refresh_token_with_invalid_refresh_token_cookie(self):
        with self.flask_application.app.app_context():
            _, session_token = SessionTokenRepo().generate_session_token(self.user_id)
            self.client.cookies = {"session-token": session_token, "refresh-token": "invalid"}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
    

    def test_refresh_token_rate_limited(self):
        get_ip = patch("Utils.utils.get_ip").start()
        get_ip.return_value = "1.1.1.1"
        with self.flask_application.app.app_context():

            self.client.cookies = {"session-token": str(uuid4()), "refresh-token": self.refresh_token}
            for _ in range(conf.features.rate_limiting.login_attempts_limit_per_ip):    
                
                response = self.client.put(self.endpoint)
                print(response.json())
                self.assertEqual(response.status_code, 401)


            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 429)
            self.assertTrue(RateLimitingRepo().is_login_rate_limited("1.1.1.1"))
            

    


    
    

