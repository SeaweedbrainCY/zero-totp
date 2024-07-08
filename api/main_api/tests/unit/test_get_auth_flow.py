import unittest
from main_api.app import app
from main_api.environment import conf
from main_api.CryptoClasses.jwt_func import generate_jwt
from main_api.controllers import flask
from unittest.mock import patch


class TestGetAuthFlow(unittest.TestCase):
    
        def setUp(self):
            if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
            self.application = app
            self.client = self.application.test_client()
            self.roleEndpoint = "/google-drive/oauth/authorization-flow"
            self.admin_user_id = 1

            self.get_authorization_url_patch = patch("main_api.Oauth.oauth_flow.get_authorization_url").start()
            self.get_authorization_url_patch.return_value = "https://www.google.com", "state"
        
        
        def test_get_auth_flow(self):
            with self.application.app.app_context():
                self.client.cookies = {"api-key":generate_jwt(self.admin_user_id)}
                response = self.client.get(self.roleEndpoint)
                self.assertEqual(response.status_code, 200)