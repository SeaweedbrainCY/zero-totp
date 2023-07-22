import os
import logging

port = int(os.environ.get('PORT')) if os.environ.get('PORT') != None else None
db_uri = os.environ.get('DATABASE_URI')
environment = "production" if os.environ.get('ENVIRONMENT') == "production" else "development"
jwt_secret = os.environ.get('JWT_SECRET')

if environment == "development":
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Environment set to development")
    frontend_domain = 'zero-totp.local'
    frontend_URI = 'http://localhost:4200'
    isCookieSecure = False
else:
    frontend_domain="zero-totp.com"
    frontend_URI = "https://zero-totp.com"
    isCookieSecure = True



if port == None:
    port = 8080
    logging.warning("PORT environment variable not set. Using default value: 8080")



if db_uri == None:
    logging.error("DATABASE_URI environment variable not set. Please set it to a valid database URI. Aborting...")
    raise Exception("DATABASE_URI environment variable not set. Please set it to a valid database URI.")





if jwt_secret == None:
    logging.error("JWT_SECRET environment variable not set. Please set it to a valid secret key. Aborting...")
    raise Exception("JWT_SECRET environment variable not set. Please set it to a valid secret key.")

