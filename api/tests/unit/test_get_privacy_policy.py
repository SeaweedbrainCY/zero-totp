import unittest
from app import app
from environment import conf, logging, PrivacyPolicyConfig
from endpoints_controllers.general import conf as controller_conf
import os


class TestGetPrivacyPolicy(unittest.TestCase):

    def setUp(self):
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/privacy-policy"

        self.default_english_privacy_policy_file = "./assets/privacy_policy/privacy_policy_en.md"
        self.default_french_privacy_policy_file = "./assets/privacy_policy/privacy_policy_fr.md"
        
            
    
    
    def test_get_default_english_privacy_policy(self):
        controller_conf.features.privacy_policy =  PrivacyPolicyConfig()
        response = self.client.get(f"{self.endpoint}?lang=en")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("content-type"), "text/markdown; charset=utf-8")
        data = response.content.decode('utf-8')
        with open(self.default_english_privacy_policy_file, "r") as f:
            expected_content = f.read()
        self.assertEqual(data, expected_content)

    def test_get_default_french_privacy_policy(self):
        controller_conf.features.privacy_policy =  PrivacyPolicyConfig()
        response = self.client.get(f"{self.endpoint}?lang=fr")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("content-type"), "text/markdown; charset=utf-8")
        data = response.content.decode('utf-8')
        with open(self.default_french_privacy_policy_file, "r") as f:
            expected_content = f.read()
        self.assertEqual(data, expected_content)

    def test_get_invalid_language_privacy_policy(self):
        controller_conf.features.privacy_policy =  PrivacyPolicyConfig()
        response = self.client.get(f"{self.endpoint}?lang=xx")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("content-type"), "text/markdown; charset=utf-8")
        data = response.content.decode('utf-8')
        with open(self.default_english_privacy_policy_file, "r") as f:
            expected_content = f.read()
        self.assertEqual(data, expected_content)

    def test_get_privacy_policy_without_language(self):
        controller_conf.features.privacy_policy =  PrivacyPolicyConfig()
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 400)
        
    
    def test_get_custom_privacy_policy_en(self):
        custom_privacy_policy_file = "./config/assets/privacy_policy/privacy_policy_en.md"
        if not os.path.exists(os.path.dirname(custom_privacy_policy_file)):
            os.makedirs(os.path.dirname(custom_privacy_policy_file))
        with open(custom_privacy_policy_file, "w") as f:
            f.write("# Custom Privacy Policy\nThis is a custom privacy policy.")
        controller_conf.features.privacy_policy =  PrivacyPolicyConfig()
        response = self.client.get(f"{self.endpoint}?lang=en")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("content-type"), "text/markdown; charset=utf-8")
        data = response.content.decode('utf-8')
        with open(custom_privacy_policy_file, "r") as f:
            expected_content = f.read()
        self.assertEqual(data, expected_content)
        os.remove(custom_privacy_policy_file)
        os.rmdir(os.path.dirname(custom_privacy_policy_file))

    def test_get_custom_privacy_policy_fr(self):
        custom_privacy_policy_file = "./config/assets/privacy_policy/privacy_policy_fr.md"
        if not os.path.exists(os.path.dirname(custom_privacy_policy_file)):
            os.makedirs(os.path.dirname(custom_privacy_policy_file))
        with open(custom_privacy_policy_file, "w") as f:
            f.write("# Politique de confidentialité personnalisée\nCeci est une politique de confidentialité personnalisée.")
        controller_conf.features.privacy_policy =  PrivacyPolicyConfig()
        response = self.client.get(f"{self.endpoint}?lang=fr")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("content-type"), "text/markdown; charset=utf-8")
        data = response.content.decode('utf-8')
        with open(custom_privacy_policy_file, "r") as f:
            expected_content = f.read()
        self.assertEqual(data, expected_content)
        os.remove(custom_privacy_policy_file)
        os.rmdir(os.path.dirname(custom_privacy_policy_file))
    
    def test_get_custom_privacy_policy_invalid_lang(self):
        custom_privacy_policy_file = "./config/assets/privacy_policy/privacy_policy_en.md"
        if not os.path.exists(os.path.dirname(custom_privacy_policy_file)):
            os.makedirs(os.path.dirname(custom_privacy_policy_file))
        with open(custom_privacy_policy_file, "w") as f:
            f.write("# Custom Privacy Policy\nThis is a custom privacy policy.")
        controller_conf.features.privacy_policy =  PrivacyPolicyConfig()
        response = self.client.get(f"{self.endpoint}?lang=xx")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("content-type"), "text/markdown; charset=utf-8")
        data = response.content.decode('utf-8')
        with open(custom_privacy_policy_file, "r") as f:
            expected_content = f.read()
        self.assertEqual(data, expected_content)
        os.remove(custom_privacy_policy_file)
        os.rmdir(os.path.dirname(custom_privacy_policy_file))