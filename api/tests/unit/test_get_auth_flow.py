import unittest
from app import app
from environment import conf
from CryptoClasses.jwt_func import generate_jwt
from controllers import flask
from unittest.mock import patch


class TestGetAuthFlow(unittest.TestCase):
    
        def setUp(self):
            if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
            self.application = app
            self.client = self.application.test_client()
            self.endpoint = "/api/v1/google-drive/oauth/authorization-flow"
            self.admin_user_id = 1

            self.get_authorization_url_patch = patch("Oauth.oauth_flow.get_authorization_url").start()
            self.get_authorization_url_patch.return_value = "https://www.google.com", "state"
        
        
        def test_get_auth_flow(self):
            with self.application.app.app_context():
                self.client.cookies = {"api-key":generate_jwt(self.admin_user_id)}
                response = self.client.get(self.endpoint)
                self.assertEqual(response.status_code, 200)