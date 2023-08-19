import os
import logging

port = int(os.environ.get('PORT')) if os.environ.get('PORT') != None else None
db_uri = os.environ.get('DATABASE_URI')
environment = "production" if os.environ.get('ENVIRONMENT') == "production" else "development"
jwt_secret = os.environ.get('JWT_SECRET')
oauth_client_secret_file = os.environ.get('OAUTH_CLIENT_SECRET_FILE')

if environment == "development":
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Environment set to development")
    frontend_domain = 'zero-totp.local'
    frontend_URI = 'http://localhost:4200'
    callback_URI = 'http://localhost:8080/oauth/callback'
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
else:
    frontend_domain="zero-totp.com"
    frontend_URI = "https://zero-totp.com"
    callback_URI = "https://zero-totp.com/callback"



if port == None:
    port = 8080
    logging.warning("PORT environment variable not set. Using default value: 8080")



if db_uri == None:
    logging.error("DATABASE_URI environment variable not set. Please set it to a valid database URI. Aborting...")
    raise Exception("DATABASE_URI environment variable not set. Please set it to a valid database URI.")





if jwt_secret == None:
    logging.error("JWT_SECRET environment variable not set. Please set it to a valid secret key. Aborting...")
    raise Exception("JWT_SECRET environment variable not set. Please set it to a valid secret key.")






if oauth_client_secret_file == None:
    logging.error("OAUTH_CLIENT_SECRET_FILE environment variable not set. Please set it to a valid path to the client_secret.json file. Aborting...")
    raise Exception("OAUTH_CLIENT_SECRET_FILE environment variable not set. Please set it to a valid path to the client_secret.json file.")