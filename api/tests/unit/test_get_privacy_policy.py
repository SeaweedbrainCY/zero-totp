import unittest
from app import app
from environment import conf


class TestGetPrivacyPolicy(unittest.TestCase):

    def setUp(self):
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/privacy-policy"
        
            
    
    
    def test_get_english_privacy_policy(self):
        response = self.client.get(f"{self.endpoint}?lang=en")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/markdown; charset=utf-8")
        data = response.get_data(as_text=True)
        with open(conf.features.privacy_policy.privacy_policy_mk_file_path["en"], "r") as f:
            expected_content = f.read()
        self.assertEqual(data, expected_content)

    def test_get_french_privacy_policy(self):
        response = self.client.get(f"{self.endpoint}?lang=fr")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/markdown; charset=utf-8")
        data = response.get_data(as_text=True)
        with open(conf.features.privacy_policy.privacy_policy_mk_file_path["fr"], "r") as f:
            expected_content = f.read()
        self.assertEqual(data, expected_content)

    def test_get_invalid_language_privacy_policy(self):
        response = self.client.get(f"{self.endpoint}?lang=xx")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/markdown; charset=utf-8")
        data = response.get_data(as_text=True)
        with open(conf.features.privacy_policy.privacy_policy_mk_file_path["en"], "r") as f:
            expected_content = f.read()
        self.assertEqual(data, expected_content)
    