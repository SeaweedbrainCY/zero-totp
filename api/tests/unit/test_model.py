import unittest
from database.model import User, ZKE_encryption_key, TOTP_secret

class TestUserConstructor(unittest.TestCase):
    def setUp(self):
        self.user = User(
            mail="test@example.com",
            password="password",
            username="testuser",
            derivedKeySalt="salt"
        )

    def test_user_attributes(self):
        self.assertEqual(self.user.mail, "test@example.com")
        self.assertEqual(self.user.password, "password")
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.derivedKeySalt, "salt")


class Testzke_encryption_keyConstructor(unittest.TestCase):

    def setUp(self):
        self.zke_encryption_key = ZKE_encryption_key(
            user_id=1,
            ZKE_key="key"
        )
    
    def test_zke_encryption_key_attributes(self):
        self.assertEqual(self.zke_encryption_key.user_id, 1)
        self.assertEqual(self.zke_encryption_key.ZKE_key, "key")


class TestTOTPSecretConstructor(unittest.TestCase):
    def setUp(self):
        self.totp_secret = TOTP_secret(
            uuid="test_uuid",
            user_id=1,
            secret_enc="test_secret_enc"
        )

    def test_totp_secret_attributes(self):
        self.assertEqual(self.totp_secret.uuid, "test_uuid")
        self.assertEqual(self.totp_secret.user_id, 1)
        self.assertEqual(self.totp_secret.secret_enc, "test_secret_enc")


if __name__ == '__main__':
    unittest.main()