from time import sleep
from app import app 
from database.db import db
from database.oauth_tokens_repo import Oauth_tokens
from CryptoClasses.encryption import ServiceSideEncryption
from environment import logging
import sys

print(sys.argv)

logging.basicConfig(level=logging.ERROR)
app.app.logger.setLevel(logging.ERROR)

# Waiting for app to initialize
sleep(2)

print("\n###### Script init done ######\n")
print("\n👋 Welcome to this utility to decrypt a database entry.\n\n")
print("######################################################")
print("#### Great power comes with great responsibility. ####")
print("####        Use this utility with caution.        ####")
print("######################################################\n\n")
print("I am explicitly allowed to execute this utility (y/N) : ", end="")
allowed = input()
if allowed.lower() != "y":
    print("\n###### Decryption utility end ######\n")
    exit(1)
print("The privacy policy and/or the user consent is respected (y/N) : ", end="")
consent = input()
if consent.lower() != "y":
    print("\n###### Decryption utility end ######\n")
    exit(1)
print("Retrieving the encrypted data from the database ... " , end='')
table_name = sys.argv[1]
if (table_name == "oauth_tokens"):
    entry_id = sys.argv[2]
    with app.app.app_context():
        oauth_tokens = Oauth_tokens()
        entry = oauth_tokens.get_by_entry_id(entry_id)
        if entry is None:
            print(f"\nEntry with id {entry_id} not found in the database.")
            exit(1)
        else:
            print("OK")
            print("Decrypting the data ... ", end='')
            sse = ServiceSideEncryption()
            decrypted = sse.decrypt(ciphertext=entry.enc_credentials, tag=entry.cipher_tag, nonce=entry.cipher_nonce)
            if decrypted is None:
                print("\n\nFailed to decrypt the data.")
                exit(1)
            print("OK")
            print("\nDecrypted data:")
            print("   - ID: ", entry.id)
            print("   - User ID: ", entry.user_id)
            print("   - Encrypted credentials: ", decrypted.decode("utf-8"))
            print("   - Expires at: ", entry.expires_at)
            print("\n###### Decryption utility done ######\n")

else:
    print("\n\nTable not supported")
    print("Supported tables:")
    print("   - oauth_tokens")
    exit(1)


