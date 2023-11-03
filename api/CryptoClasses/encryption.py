from Crypto.Cipher import AES
import environment as env
from base64 import b64encode, b64decode
import json
from environment import logging


class ServiceSideEncryption:
    def __init__(self) -> None:
      self.key = b64decode(env.sever_side_encryption_key)


    def encrypt(self, message) -> dict :
        data = message.encode("utf-8")
        cipher = AES.new(self.key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        encrypted_data = {"ciphertext": b64encode(ciphertext).decode("utf-8"), "nonce": b64encode(cipher.nonce).decode("utf-8"), "tag": b64encode(tag).decode("utf-8")}
        return  encrypted_data
    
    def decrypt(self, json_cipher) -> str or None:
        try:
            json_cipher = json.loads(json_cipher)
        except Exception as e:
            logging.warning("Invalid json cipher : " + str(e))
            return None
        try:
            cipher = AES.new(self.key, AES.MODE_EAX, b64decode(json_cipher["nonce"]))

            plaintext = cipher.decrypt(b64decode(json_cipher["ciphertext"]))
        
            cipher.verify(b64decode(json_cipher["tag"]))
            return plaintext.decode("utf-8")
        except (ValueError , KeyError) as e:
            logging.error("Invalid decryption : " + str(e))
            return None
    
