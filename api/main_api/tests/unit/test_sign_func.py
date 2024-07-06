import unittest
from  main_api.CryptoClasses.sign_func import API_signature


class TestBcrypt(unittest.TestCase):
    
    def setUp(self):
        self.api_signature = API_signature()

    def test_signature(self):
        message = "Hello World"
        signature = self.api_signature.sign_rsa(message)
        self.assertTrue(signature)
    
    def test_verifying(self):
        message = "Hello World"
        signature = self.api_signature.sign_rsa(message)
        self.assertTrue(signature)
        self.assertTrue(self.api_signature.verify_rsa_signature(message=message, signature=signature))
    
    def test_verifying_wrong_message(self):
        message = "Hello World"
        signature = self.api_signature.sign_rsa(message)
        self.assertTrue(signature)
        self.assertFalse(self.api_signature.verify_rsa_signature(message="Hello World!", signature=signature))
    
    def test_verifying_wrong_signature(self):
        message = "Hello World"
        signature = self.api_signature.sign_rsa(message)
        self.assertTrue(signature)
        self.assertFalse(self.api_signature.verify_rsa_signature(message=message, signature="3273a3e8fd23c695671ed7c7d10baa5ae2651c3f0ea5f44"))