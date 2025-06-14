import unittest
from app import app
from environment import conf
from unittest.mock import patch
from environment import logging


class TestGetVaultSignaturePublicKey(unittest.TestCase):

    def setUp(self):
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/vault/signature/public-key"
        
            
 
    
    
    def test_get_vault_signature_public_key(self):
        """
        Test the /vault/signature/public-key endpoint
        Path defined in test file
        """
        with open("./tests/ressources/test_public.pem", "r") as f:
            public_key = f.read()
        with self.flask_application.app.app_context():
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["public_key"], public_key)

    def test_get_vault_signature_attempting_fetch_private_key(self):
        old_public_key_path = conf.api.public_key_path
        conf.api.public_key_path = conf.api.private_key_path
        with self.flask_application.app.app_context():
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
        conf.api.public_key_path = old_public_key_path
            

    def test_get_vault_signature_attempting_fetch_invalid_public_key(self):
        with open("./tests/ressources/test_public.pem", "r") as f:
            original_content = f.read()
        with open("./tests/ressources/test_public.pem", "w") as f:
            f.write("invalid public key")
        with self.flask_application.app.app_context():
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
        with open("./tests/ressources/test_public.pem", "w") as f:
            f.write(original_content)



