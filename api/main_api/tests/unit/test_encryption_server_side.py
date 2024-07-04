import unittest
from CryptoClasses.encryption import ServiceSideEncryption


class TestEncryptionServerSide(unittest.TestCase):
    
    def setUp(self):
        self.server_side_encryption = ServiceSideEncryption()

    def test_encryption_decryption(self):
        message = "hello world"
        encrypted_data = self.server_side_encryption.encrypt(message)
        self.assertEqual(message, self.server_side_encryption.decrypt(encrypted_data["ciphertext"], encrypted_data["tag"], encrypted_data["nonce"]))
    
    def test_invalid_ciphertext(self):
        message = "hello world"
        encrypted_data = self.server_side_encryption.encrypt(message)
        self.assertIsNone(self.server_side_encryption.decrypt("invalid ciphertext", encrypted_data["tag"], encrypted_data["nonce"]))
    
    def test_invalid_tag(self):
        message = "hello world"
        encrypted_data = self.server_side_encryption.encrypt(message)
        self.assertIsNone(self.server_side_encryption.decrypt(encrypted_data["ciphertext"], "invalid tag", encrypted_data["nonce"]))

    def test_invalid_nonce(self):
        message = "hello world"
        encrypted_data = self.server_side_encryption.encrypt(message)
        self.assertIsNone(self.server_side_encryption.decrypt(encrypted_data["ciphertext"], encrypted_data["tag"], "invalid nonce"))
    
    def test_invalid_key(self):
        message = "hello world"
        encrypted_data = self.server_side_encryption.encrypt(message)
        self.server_side_encryption.key = "invalid key"
        self.assertIsNone(self.server_side_encryption.decrypt(encrypted_data["ciphertext"], encrypted_data["tag"], encrypted_data["nonce"]))
    
        
