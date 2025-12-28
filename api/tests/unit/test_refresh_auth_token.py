import unittest
from app import app
from database.db import db 
from environment import conf
from zero_totp_db_model.model import User as UserModel, SessionToken
from database.refresh_token_repo import RefreshTokenRepo
from database.rate_limiting_repo import RateLimitingRepo
from database.session_token_repo import SessionTokenRepo
from database.session_repo import SessionRepo
from database.user_repo import User as UserRepo
from unittest.mock import patch
import datetime
from uuid import uuid4
from hashlib import sha256
from environment import logging
from Utils import utils
import datetime as dt
from freezegun import freeze_time


class TestRefreshAuthToken(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/auth/refresh"
        self.user_id = 1
        self.user2_id = 2
        with self.flask_application.app.app_context():
            user = UserModel(id=self.user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = False, passphraseSalt = "AAAA", createdAt="01/01/2001")
            _ = UserModel(id=self.user2_id,username="user2", mail="user2@user.com", password="pass2", derivedKeySalt="BBB", isVerified = False, passphraseSalt = "BBBB", createdAt="01/01/2001")
            db.create_all()
            db.session.add(user)
            db.session.commit()
            self.session_token, self.refresh_token = utils.generate_new_session(user=user, ip_address=None)
            self.hashed_refresh_token = sha256(self.refresh_token.encode('utf-8')).hexdigest()
        
        self.session_token_expiration_date = dt.datetime.now(dt.UTC) + dt.timedelta(seconds=conf.api.session_token_validity)
        self.refresh_token_expiration_date = dt.datetime.now(dt.UTC) + dt.timedelta(seconds=conf.api.refresh_token_validity)
        self.session_expiration_date = dt.datetime.now(dt.UTC) + dt.timedelta(seconds=conf.api.session_validity)
 
       
    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()


    
    def test_refresh_token(self):
        with self.flask_application.app.app_context():
            old_session = SessionTokenRepo().get_session_token(self.session_token).session
            self.client.cookies = {"session-token": self.session_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Set-Cookie", response.headers)
            self.assertIn("session-token", response.headers["Set-Cookie"])
            self.assertIn("refresh-token", response.headers["Set-Cookie"])
            cookies = response.headers["Set-Cookie"].split("session-token=")
            self.assertEqual(len(cookies), 2, "Session-token found multiple times in the response")
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

            
            old_session_token_entry = SessionTokenRepo().get_session_token(self.session_token)
            old_refresh_token_entry = RefreshTokenRepo().get_refresh_token_by_hash(self.hashed_refresh_token)
            new_hashed_refresh_token = sha256(refresh_token_cookie.split(";")[0].encode('utf-8')).hexdigest()
            new_refresh_token_entry = RefreshTokenRepo().get_refresh_token_by_hash(new_hashed_refresh_token)
            new_session_token_entry = SessionTokenRepo().get_session_token_by_id(new_refresh_token_entry.session_token_id)

            # Ensure new tokens still belongs to the same session and to the same user
            self.assertEqual(old_session.id, new_session_token_entry.session.id)
            self.assertEqual(old_session.id, new_refresh_token_entry.session.id)
            self.assertEqual(self.user_id, new_session_token_entry.user_id)
            self.assertEqual(self.user_id, new_refresh_token_entry.user_id)

            # Verify refresh token is linked to the new session token
            self.assertEqual(new_refresh_token_entry.session_token_id, new_session_token_entry.id)

            # Verify the old tokens are revoked and new ones are valid
            self.assertLess(float(old_refresh_token_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(old_session_token_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())

            # Verify the new tokens expiration is correct
            self.assertLess(dt.datetime.now(dt.UTC) - dt.datetime.fromtimestamp(float(new_session_token_entry.expiration), dt.UTC) + dt.timedelta(seconds=conf.api.session_token_validity) , dt.timedelta(seconds=5))
            self.assertLess(dt.datetime.now(dt.UTC) - dt.datetime.fromtimestamp(float(new_refresh_token_entry.expiration), dt.UTC) + dt.timedelta(seconds=conf.api.refresh_token_validity)  , dt.timedelta(seconds=5))

            # Verify the session expiration didn't change, is not revoked and last active timestamp is updated
            self.assertEqual(old_session.expiration_timestamp, new_session_token_entry.session.expiration_timestamp)
            self.assertIsNone(new_session_token_entry.session.revoke_timestamp)
            self.assertLess(float(new_session_token_entry.session.last_active_at) - dt.datetime.now(dt.UTC).timestamp(), 5)

            # Verify cookies contains the new tokens
            self.assertIn(new_session_token_entry.token, session_token_cookie)
            self.assertIn(new_refresh_token_entry.hashed_token, new_hashed_refresh_token)

            
    def test_refresh_token_with_expired_session_token(self):
        with freeze_time((self.session_token_expiration_date + dt.timedelta(seconds=1))):
            with self.flask_application.app.app_context():
                old_session = SessionTokenRepo().get_session_token(self.session_token).session
                self.client.cookies = {"session-token": self.session_token, "refresh-token": self.refresh_token}
                response = self.client.put(self.endpoint)
                self.assertEqual(response.status_code, 200)
                self.assertIn("Set-Cookie", response.headers)
                self.assertIn("session-token", response.headers["Set-Cookie"])
                self.assertIn("refresh-token", response.headers["Set-Cookie"])
                cookies = response.headers["Set-Cookie"].split("session-token=")
                self.assertEqual(len(cookies), 2, "Session-token found multiple times in the response")
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


                old_session_token_entry = SessionTokenRepo().get_session_token(self.session_token)
                old_refresh_token_entry = RefreshTokenRepo().get_refresh_token_by_hash(self.hashed_refresh_token)
                new_hashed_refresh_token = sha256(refresh_token_cookie.split(";")[0].encode('utf-8')).hexdigest()
                new_refresh_token_entry = RefreshTokenRepo().get_refresh_token_by_hash(new_hashed_refresh_token)
                new_session_token_entry = SessionTokenRepo().get_session_token_by_id(new_refresh_token_entry.session_token_id)

                # Ensure new tokens still belongs to the same session and to the same user
                self.assertEqual(old_session.id, new_session_token_entry.session.id)
                self.assertEqual(old_session.id, new_refresh_token_entry.session.id)
                self.assertEqual(self.user_id, new_session_token_entry.user_id)
                self.assertEqual(self.user_id, new_refresh_token_entry.user_id)

                # Verify refresh token is linked to the new session token
                self.assertEqual(new_refresh_token_entry.session_token_id, new_session_token_entry.id)

                # Verify the old tokens are revoked and new ones are valid
                self.assertLess(float(old_refresh_token_entry.revoke_timestamp), dt.datetime.now(dt.UTC).timestamp())
                self.assertLess(float(old_session_token_entry.revoke_timestamp), dt.datetime.now(dt.UTC).timestamp())

                # Verify the new tokens expiration is correct
                self.assertLess(dt.datetime.fromtimestamp(float(new_session_token_entry.expiration), dt.UTC) + dt.timedelta  (seconds=conf.api.session_token_validity) - dt.datetime.now(dt.UTC), dt.timedelta(seconds=5))
                self.assertLess(dt.datetime.fromtimestamp(new_refresh_token_entry.expiration, dt.UTC) + dt.timedelta    (seconds=conf.api.refresh_token_validity) - dt.datetime.now(dt.UTC), dt.timedelta(seconds=5))

                # Verify the session expiration didn't change, is not revoked and last active timestamp is updated
                self.assertEqual(old_session.expiration_timestamp, new_session_token_entry.session.expiration_timestamp)
                self.assertIsNone(new_session_token_entry.session.revoke_timestamp)
                self.assertLess(float(new_session_token_entry.session.last_active_at) - dt.datetime.now(dt.UTC). timestamp(), 5)

                # Verify cookies contains the new tokens
                self.assertIn(new_session_token_entry.token, session_token_cookie)
                self.assertIn(new_refresh_token_entry.token, refresh_token_cookie)
    
    def test_refresh_token_same_user_token_but_unpaired_good_session_bad_refresh(self):
         with self.flask_application.app.app_context():
            user = UserRepo().getById(self.user_id)
            session_token2, refresh_token2 = utils.generate_new_session(user, ip_address=None)

            hashed_refresh_token2 = sha256(refresh_token2.encode('utf-8')).hexdigest()

            self.client.cookies = {"session-token": self.session_token, "refresh-token": refresh_token2}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)

            session_token_entry = SessionTokenRepo().get_session_token(self.session_token)
            refresh_token_entry = RefreshTokenRepo().get_refresh_token_by_hash(self.hashed_refresh_token)
            session_token2_entry = SessionTokenRepo().get_session_token(session_token2)
            refresh_token2_entry = RefreshTokenRepo().get_refresh_token_by_hash(hashed_refresh_token2)

            self.assertLess(float(refresh_token_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(session_token_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(session_token2_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(refresh_token2_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(session_token_entry.session.last_active_at) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(session_token2_entry.session.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())

    def test_refresh_token_same_user_token_but_unpaired_bad_session_good_refresh(self):
         with self.flask_application.app.app_context():
            user = UserRepo().getById(self.user_id)
            session_token2, refresh_token2 = utils.generate_new_session(user, ip_address=None)

            hashed_refresh_token2 = sha256(refresh_token2.encode('utf-8')).hexdigest()

            self.client.cookies = {"session-token": session_token2, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)

            session_token_entry = SessionTokenRepo().get_session_token(self.session_token)
            refresh_token_entry = RefreshTokenRepo().get_refresh_token_by_hash(self.hashed_refresh_token)
            session_token2_entry = SessionTokenRepo().get_session_token(session_token2)
            refresh_token2_entry = RefreshTokenRepo().get_refresh_token_by_hash(hashed_refresh_token2)

            self.assertLess(float(session_token_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(refresh_token_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp(), )
            self.assertLess(float(session_token2_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(refresh_token2_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(session_token_entry.session.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            

    
    def test_refresh_token_with_refresh_token_from_other_user(self):
         with self.flask_application.app.app_context():
            user2 = UserRepo().getById(self.user2_id)

            user2_session_token, user2_refresh_token = utils.generate_new_session(user2, ip_address=None)
            user2_hashed_refresh_token = sha256(user2_refresh_token.encode('utf-8')).hexdigest()

            user1_session_token_entry = SessionTokenRepo().get_session_token(self.session_token)
            user1_refresh_token_entry = RefreshTokenRepo().get_refresh_token_by_hash(self.hashed_refresh_token)

            user2_session_token_entry = SessionTokenRepo().get_session_token(user2_session_token)
            user2_refresh_token_entry = RefreshTokenRepo().get_refresh_token_by_hash(user2_hashed_refresh_token)

            self.client.cookies = {"session-token": self.session_token, "refresh-token": user2_refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertLess(float(user1_session_token_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(user1_refresh_token_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(user2_session_token_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(user2_refresh_token_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(user1_session_token_entry.session.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(user2_session_token_entry.session.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
    
    def test_refresh_token_with_session_token_from_other_user(self):
         with self.flask_application.app.app_context():
            user2 = UserRepo().getById(self.user2_id)

            user2_session_token, user2_refresh_token = utils.generate_new_session(user2, ip_address=None)
            user2_hashed_refresh_token = sha256(user2_refresh_token.encode('utf-8')).hexdigest()

            user1_session_token_entry = SessionTokenRepo().get_session_token(self.session_token)
            user1_refresh_token_entry = RefreshTokenRepo().get_refresh_token_by_hash(self.hashed_refresh_token)

            user2_session_token_entry = SessionTokenRepo().get_session_token(user2_session_token)
            user2_refresh_token_entry = RefreshTokenRepo().get_refresh_token_by_hash(user2_hashed_refresh_token)

            self.client.cookies = {"session-token": user2_session_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertLess(float(user1_session_token_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(user1_refresh_token_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(user2_session_token_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(user2_refresh_token_entry.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(user1_session_token_entry.session.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())
            self.assertLess(float(user2_session_token_entry.session.revoke_timestamp) , dt.datetime.now(dt.UTC).timestamp())

    def test_refresh_token_with_expired_session(self):
        with self.flask_application.app.app_context():
            with freeze_time((self.session_expiration_date + dt.timedelta(seconds=1))):
                self.client.cookies = {"session-token":self.session_token, "refresh-token": self.refresh_token}
                response = self.client.put(self.endpoint)
                self.assertEqual(response.status_code, 403)

    def test_refresh_token_with_revoked_session(self):
        with self.flask_application.app.app_context():
            session_entry = SessionTokenRepo().get_session_token(self.session_token).session
            SessionRepo().revoke(session_entry.id)
            self.client.cookies = {"session-token":self.session_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)



    def test_refresh_token_with_expired_refresh_token(self):
        with self.flask_application.app.app_context():
            with freeze_time((self.refresh_token_expiration_date + dt.timedelta(seconds=1))):
                self.client.cookies = {"session-token":self.session_token, "refresh-token": self.refresh_token}
                response = self.client.put(self.endpoint)
                self.assertEqual(response.status_code, 403)
    
    def test_refresh_token_with_revoked_refresh_token(self):
        with self.flask_application.app.app_context():
            refresh_token_entry = RefreshTokenRepo().get_refresh_token_by_hash(self.hashed_refresh_token)
            RefreshTokenRepo().revoke(refresh_token_entry.id)
            self.client.cookies = {"session-token":self.session_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)

    def test_refresh_token_with_revoked_session_token(self):
        with self.flask_application.app.app_context():
            session_token_entry = SessionTokenRepo().get_session_token(self.session_token)
            RefreshTokenRepo().revoke(session_token_entry.id)
            self.client.cookies = {"session-token":self.session_token, "refresh-token": self.refresh_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_refresh_token_with_unknown_refresh_token(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token, "refresh-token": str(uuid4())}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 403)
    
    def test_refresh_token_with_no_refresh_token(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 401)
    
    def test_refresh_token_with_no_session_token(self):
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
            self.client.cookies = {"session-token": self.session_token, "refresh-token": "invalid"}
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
            

    


    
    

