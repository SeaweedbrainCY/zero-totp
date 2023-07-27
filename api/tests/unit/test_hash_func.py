import unittest
from Crypto.hash_func import Bcrypt

class TestBcrypt(unittest.TestCase):
    
    def setUp(self):
        self.bcrypt = Bcrypt("password")

    def test_password_too_long(self):
        self.bcrypt.password = "a" * 73
        self.assertRaises(ValueError, self.bcrypt.hashpw)

if __name__ == '__main__':
    unittest.main()