import unittest
import controllers
from app import create_app
from unittest.mock import patch
from database.user_repo import User as UserRepo
from database.oauth_tokens_repo import Oauth_tokens as OAuthTokensRepo
from database.google_drive_integration_repo import GoogleDriveIntegration as GoogleDriveIntegrationRepo
import environment as env
from CryptoClasses import jwt_func
import jwt
import datetime
from database.db import db

class TestGoogleDriveOption(unittest.TestCase):

    def setUp(self):
        env.db_uri = "sqlite:///:memory:"
        self.app = create_app()
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.app.test_client()
        self.endpoint = "/google-drive/option"

        self.user_repo = UserRepo()
        self.google_integration = GoogleDriveIntegrationRepo()
        with self.app.app_context():
            db.create_all()
            self.user_repo.create(username="user", email="user@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now())
            db.session.commit()
            


    def tearDown(self):
        patch.stopall()
    
    def generate_expired_cookie(self):
        payload = {
            "iss": jwt_func.ISSUER,
            "sub": 1,
            "iat": datetime.datetime.utcnow(),
            "nbf": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() - datetime.timedelta(hours=1),
        }
        jwtCookie = jwt.encode(payload, env.jwt_secret, algorithm=jwt_func.ALG)
        return jwtCookie
    
    def test_google_drive_option(self):
        with self.app.app_context():
            self.google_integration.create(user_id=1, google_drive_sync=True)
            self.client.set_cookie("localhost", "api-key", self.jwtCookie)
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["status"], "enabled")

    def test_google_drive_option_disabled(self):
        with self.app.app_context():
            self.google_integration.create(user_id=1, google_drive_sync=False)
            self.client.set_cookie("localhost", "api-key", self.jwtCookie)
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["status"], "disabled")

    def test_google_drive_option_doesnt_exists(self):
        with self.app.app_context():
            self.client.set_cookie("localhost", "api-key", self.jwtCookie)
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["status"], "disabled")
    
    def test_google_drive_no_cookie(self):
        with self.app.app_context():
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 401)

    def test_google_drive_bad_cookie(self):
         with self.app.app_context():
            self.client.set_cookie("localhost", "api-key", "badcookie")
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)

   
  