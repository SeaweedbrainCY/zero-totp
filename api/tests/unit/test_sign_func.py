import unittest
from  CryptoClasses.sign_func import sign


class TestBcrypt(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_signature(self):
        message = "Hello World"
        signature = sign(message)
        print(message, signature)
        self.assertTrue(signature)