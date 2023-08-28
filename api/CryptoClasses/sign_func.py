from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import environment as env


def sign(message):
    with open(env.private_key_path, "r") as key_file:
        private_key = RSA.import_key(key_file.read())
        h = SHA256.new(message.encode())
        signature = pkcs1_15.new(private_key).sign(h)
        return signature.hex()
    