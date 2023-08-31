import unittest
from  CryptoClasses.sign_func import sign, verify


class TestBcrypt(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_signature(self):
        message = "Hello World"
        signature = sign(message)
        self.assertTrue(signature)
    
    def test_verifying(self):
        message = "Hello World"
        signature = sign(message)
        self.assertTrue(signature)
        self.assertTrue(verify(message=message, signature=signature))
    
    def test_verifying_wrong_message(self):
        message = "Hello World"
        signature = sign(message)
        self.assertTrue(signature)
        self.assertFalse(verify(message="Hello World!", signature=signature))
    
    def test_verifying_wrong_signature(self):
        message = "Hello World"
        signature = sign(message)
        self.assertTrue(signature)
        self.assertFalse(verify(message=message, signature="3273a3e8fd23c695671ed7c7d10baa5ae2651c3f0ea5f44"))