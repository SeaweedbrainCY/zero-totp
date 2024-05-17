from Crypto.PublicKey import RSA
import os

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
        
