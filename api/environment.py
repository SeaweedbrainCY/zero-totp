import os
import logging

port = int(os.environ.get('PORT')) if os.environ.get('PORT') != None else None
if port == None:
    port = 8080
    logging.warning("PORT environment variable not set. Using default value: 8080")
db_uri = os.environ.get('DATABASE_URI')
if db_uri == None:
    logging.error("DATABASE_URI environment variable not set. Please set it to a valid database URI. Aborting...")
    raise Exception("DATABASE_URI environment variable not set. Please set it to a valid database URI.")
