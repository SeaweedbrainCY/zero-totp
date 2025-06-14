from Crypto.PublicKey import RSA
import os
from environment import logging

class ServerRSAKeys:
    def generate(self, private_key_path:str, public_key_path:str):
        key = RSA.generate(4096)
        private_key = key.export_key()
        public_key = key.publickey().export_key()

        os.makedirs(os.path.dirname(private_key_path), exist_ok=True)
        os.makedirs(os.path.dirname(public_key_path), exist_ok=True)

        with open(private_key_path, "wb") as f:
            f.write(private_key)
        with open(public_key_path, "wb") as f:
            f.write(public_key)
        
        os.chmod(private_key_path, 0o600)

    
    def validate_rsa_public_key(self, public_key_str:str):
        try:
            key = RSA.import_key(public_key_str)
            if key.has_private():
                logging.error("CRITICAL ERROR: An attempt to validate a public has been made and resulted in a private key. This error might be the sign of an ongoing compromise. Validation has been rejected.")
                return False 
            return True
        except (ValueError, TypeError) as e:
            return False
        
