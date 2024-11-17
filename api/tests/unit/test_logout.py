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


class TestLogout(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/logout"
        self.user_id = 1
        self.jwt_token = generate_jwt(self.user_id)
        with self.flask_application.app.app_context():
            user = UserModel(id=self.user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001")
            db.create_all()
            db.session.add(user)
            db.session.commit()
        self.jti = verify_jwt(self.jwt_token)["jti"]
        self.refresh_token = str(uuid4())
        self.hashed_refresh_token = sha256(self.refresh_token.encode('utf-8')).hexdigest()
        with self.flask_application.app.app_context():
            RefreshTokenRepo().create_refresh_token(self.user_id, self.jti,self.hashed_refresh_token)
 
       
    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()
    
    def generate_jwt_expired(self, user_id):
        jti = str(uuid4())
        try:
            payload = {
                "iss": ISSUER,
                "sub": user_id,
                "iat": datetime.datetime.now(datetime.UTC),
                "nbf": datetime.datetime.now(datetime.UTC),
                "exp": datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=conf.api.access_token_validity),
                "jti": jti
            }
            return jwt.encode(payload, conf.api.jwt_secret, algorithm=ALG), jti
        except Exception as e:
            logging.warning("Error while generating JWT : " + str(e))
            raise e
    
    def test_logout(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key": self.jwt_token}
            response = self.client.put(self.endpoint)
            print(response.json())
            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(RefreshTokenRepo().get_refresh_token_by_jti(self.jti).revoke_timestamp)

    
    def test_logout_no_jwt(self):
        with self.flask_application.app.app_context():
            response = self.client.put(self.endpoint)
            self.assertEqual(response.status_code, 401)


