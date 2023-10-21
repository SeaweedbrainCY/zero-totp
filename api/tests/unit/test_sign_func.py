import unittest
from  CryptoClasses.sign_func import API_signature, AdminSignature


class TestBcrypt(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_signature(self):
        message = "Hello World"
        signature = API_signature.sign_rsa(message)
        self.assertTrue(signature)
    
    def test_verifying(self):
        message = "Hello World"
        signature = API_signature.sign_rsa(message)
        self.assertTrue(signature)
        self.assertTrue(API_signature.verify_rsa_signature(message=message, signature=signature))
    
    def test_verifying_wrong_message(self):
        message = "Hello World"
        signature = API_signature.sign_rsa(message)
        self.assertTrue(signature)
        self.assertFalse(API_signature.verify_rsa_signature(message="Hello World!", signature=signature))
    
    def test_verifying_wrong_signature(self):
        message = "Hello World"
        signature = API_signature.sign_rsa(message)
        self.assertTrue(signature)
        self.assertFalse(API_signature.verify_rsa_signature(message=message, signature="3273a3e8fd23c695671ed7c7d10baa5ae2651c3f0ea5f44"))