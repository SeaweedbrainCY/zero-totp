from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import environment as env
import logging


def sign(message):
    with open(env.private_key_path, "r") as key_file:
        private_key = RSA.import_key(key_file.read())
        h = SHA256.new(message.encode())
        signature = pkcs1_15.new(private_key).sign(h)
        return signature.hex()


def verify(signature, message):
    with open(env.public_key_path, "r") as key_file:
        public_key = RSA.import_key(key_file.read())
        h = SHA256.new(message.encode("utf-8"))
        try:
            signature = bytes.fromhex(signature)
            pkcs1_15.new(public_key).verify(h, signature)
            return True  
        except (ValueError, TypeError) as e:
            logging.warning("Invalid signature " + str(e))
            return False  