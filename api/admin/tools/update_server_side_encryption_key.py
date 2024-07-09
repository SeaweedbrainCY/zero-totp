from getpass import getpass
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512
from app import app 
from database.db import db
from base64 import b64decode


print("Welcome to this utility to update the server side encryption key.")
print("You can use this utility to re-encrypt your database stored data with a new key.")
print("This is useful if you want to rotate your keys.")
print("Please make sure to backup your database before running this utility.\n")
print("Did you backup your database? (y/N) : ", end="")
backup = input()
if backup.lower() != "y":
    print("Please backup your database before running this utility.")
    exit(1)


new_key = getpass(prompt="Please enter your new server side encryption key:")
new_key_confirm = getpass(prompt="Please confirm your new server side encryption key:")

if new_key != new_key_confirm:
    print("The new key and the confirmation key do not match.")
    exit(1)

print("Updating the server side encryption key...")
print("DO NOT INTERRUPT THIS PROCESS. THIS COULD LEAD TO DATA LOSS.")


# update encrypted oauth creds 

from zero_totp_db_model.model import Oauth_tokens
from CryptoClasses.encryption import ServiceSideEncryption
new_aes_key = PBKDF2(new_key.encode("utf-8"), '4ATK7mA8aKgT6768' , count=2000000, dkLen=32, hmac_hash_module=SHA512)

old_sse = ServiceSideEncryption()
new_sse = ServiceSideEncryption()
new_sse.key = new_aes_key
with app.app.app_context():
    all_enc_creds = db.session.query(Oauth_tokens).all()
    for enc_cred in all_enc_creds:
        decrypted = old_sse.decrypt(ciphertext=enc_cred.enc_credentials, tag=enc_cred.cipher_tag, nonce=enc_cred.cipher_nonce)
        if decrypted is None:
            print(f"Failed to decrypt oauth token for user {enc_cred.user_id}")
            continue
        new_encrypted = new_sse.encrypt(decrypted)
        enc_cred.enc_credentials = new_encrypted["ciphertext"]
        enc_cred.cipher_nonce = new_encrypted["nonce"]
        enc_cred.cipher_tag = new_encrypted["tag"]
        db.session.commit()


print("Server side encryption key updated successfully.")
print("You can now update the server side encryption key in the configuration file.")


