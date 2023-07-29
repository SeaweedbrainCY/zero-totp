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

    def test_hashpw_same_pw(self):
        self.assertEqual(self.bcrypt.hashpw(), bcrypt.hashpw("password".encode("utf-8"), self.salt))
    
    def test_hashpw_diff_pw(self):
        self.assertNotEqual(self.bcrypt.hashpw(), bcrypt.hashpw("wrongpassword".encode("utf-8"), self.salt))

    def test_checkpw_correct(self):
        self.assertTrue(self.bcrypt.checkpw(bcrypt.hashpw("password".encode("utf-8"), self.salt).decode("utf-8")))
    
    def test_checkpw_incorrect(self):
        self.assertFalse(self.bcrypt.checkpw(bcrypt.hashpw("wrongpassword".encode("utf-8"), self.salt).decode("utf-8")))
    
    def test_checkpw_incorrect_type(self):
        falsePassword =  "a" * 73
        self.assertFalse(self.bcrypt.checkpw( falsePassword))


if __name__ == '__main__':
    unittest.main()