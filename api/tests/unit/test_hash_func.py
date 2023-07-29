import unittest
from Crypto.hash_func import Bcrypt
import bcrypt

class TestBcrypt(unittest.TestCase):
    
    def setUp(self):
        self.bcrypt = Bcrypt("password")
        self.salt = self.bcrypt.salt

    def test_password_too_long(self):
        self.bcrypt.password = "a" * 73
        self.assertRaises(ValueError, self.bcrypt.hashpw)

    def test_hashpw(self):
        self.assertEqual(self.bcrypt.hashpw(), bcrypt.hashpw("password".encode("utf-8"), self.salt))
        self.assertNotEqual(self.bcrypt.hashpw(), bcrypt.hashpw("wrongpassword".encode("utf-8"), self.salt))

    def test_checkpw(self):
        self.assertTrue(self.bcrypt.checkpw(bcrypt.hashpw("password".encode("utf-8"), self.salt).decode("utf-8")))
        self.assertFalse(self.bcrypt.checkpw(bcrypt.hashpw("wrongpassword".encode("utf-8"), self.salt).decode("utf-8")))

if __name__ == '__main__':
    unittest.main()