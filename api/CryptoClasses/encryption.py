from Crypto.Cipher import AES
from base64 import b64encode, b64decode
import json
from environment import logging, conf
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512

class ServiceSideEncryption:
    def __init__(self) -> None:
      self.key = PBKDF2(conf.api.server_side_encryption_key.encode("utf-8"), '4ATK7mA8aKgT6768' , count=2000000, dkLen=32, hmac_hash_module=SHA512)


    def encrypt(self, message) -> dict :
        data = message.encode("utf-8")
        cipher = AES.new(self.key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        encrypted_data = {"ciphertext": b64encode(ciphertext).decode("utf-8"), "nonce": b64encode(cipher.nonce).decode("utf-8"), "tag": b64encode(tag).decode("utf-8")}
        return  encrypted_data
    
    def decrypt(self, ciphertext, tag, nonce) -> str or None:
        try:
            cipher = AES.new(self.key, AES.MODE_EAX, b64decode(nonce))

            plaintext = cipher.decrypt(b64decode(ciphertext))
        
            cipher.verify(b64decode(tag))
            return plaintext.decode("utf-8")
        except (ValueError , KeyError) as e:
            logging.error("Invalid decryption : " + str(e))
            return None
    
