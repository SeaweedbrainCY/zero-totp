import unittest
from app import app
from environment import conf
import os
from unittest.mock import patch


class TestGetConfiguration(unittest.TestCase):

    def setUp(self):
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/configuration"

    def test_get_configuration(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("signup_enabled", data)
        self.assertIsInstance(data["signup_enabled"], bool)

    def test_get_configuration_when_signup_disabled(self):
        with patch.object(conf.features, 'signup_enabled', False):
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertFalse(data["signup_enabled"])