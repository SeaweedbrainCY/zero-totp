from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import environment as env
import logging
import base64
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA384

# Signature and verifications performed BY the API with the API's keys
class API_signature:
    def sign_rsa(self, message):
        with open(env.private_key_path, "r") as key_file:
            private_key = RSA.import_key(key_file.read())
            h = SHA256.new(message.encode())
            signature = pkcs1_15.new(private_key).sign(h)
            return base64.b64encode(signature).decode("utf-8")

    def verify_rsa_signature(self,signature, message):
        with open(env.public_key_path, "r") as key_file:
            public_key = RSA.import_key(key_file.read())
            h = SHA256.new(message.encode("utf-8"))
            try:
                signature = base64.b64decode(signature)
                pkcs1_15.new(public_key).verify(h, signature)
                return True  
            except (ValueError, TypeError) as e:
                logging.warning("Invalid signature " + str(e))
                return False  

# Signature and verifications performed BY an admin on the frontend and verified by the API with the admin's public key
class AdminSignature:
    def verify_ecdsa_signature(self,message, signature, public_key_b64):
        public_key_pem = "-----BEGIN PUBLIC KEY-----\n" + public_key_b64 + "\n-----END PUBLIC KEY-----"
        public_key = ECC.import_key(public_key_pem)
        h = SHA384.new(message)
        verification = DSS.new(public_key, 'fips-186-3', 'der')
        try:
            verification.verify(h, signature)
            return True
        except (ValueError, TypeError) as e:
            logging.warning("Invalid signature " + str(e))
            return False

