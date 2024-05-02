import os
import logging
import pyyaml 

# TODO : add requirements for each value

class EnvironmentConfig:
    def __init__(self, env) -> None:
        if env == "local":
            self.type = "local"
            logging.basicConfig(
                format='%(asctime)s %(levelname)-8s %(message)s',
                level=logging.DEBUG,
                datefmt='%d-%m-%Y %H:%M:%S')
            logging.debug("Environment set to development")
            self.frontend_domain = 'zero-totp.local'
            self.frontend_URI = ['http://localhost:4200']
            self.callback_URI = 'http://localhost:8080/google-drive/oauth/callback'
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        elif env == "development":
            self.type = "development"
            logging.basicConfig(
                format='%(asctime)s %(levelname)-8s %(message)s',
                level=logging.INFO,
                datefmt='%d-%m-%Y %H:%M:%S')
            logging.info("Environment set to development")
            self.frontend_domain = 'dev.zero-totp.com'
            self.frontend_URI = ['https://dev.zero-totp.com']
            self.callback_URI = "https://dev.zero-totp.com/google-drive/oauth/callback"
        else:
            self.type = "production"
            logging.basicConfig(
                filename="/var/log/api/api.log",
                filemode='a',
                format='%(asctime)s %(levelname)-8s %(message)s',
                level=logging.INFO,
                datefmt='%d-%m-%Y %H:%M:%S')
            self.frontend_domain="zero-totp.com"
            self.frontend_URI = ["https://zero-totp.com", "https://ca.zero-totp.com", "https://eu.zero-totp.com"]
            self.callback_URI = "https://api.zero-totp.com/google-drive/oauth/callback"

class OauthConfig:
    required_keys = ["client_secret_file_path"]

    def __init__(self, data):
        for key in self.required_keys:
            if key not in data:
                logging.error(f"Was expecting the key api.oauth.'{key}'")
                raise Exception(f"Was expecting the key api.oauth.'{key}'")
        self.client_secret_file_path = data["client_secret_file_path"]

class APIConfig:
    required_keys = ["database_uri", "jwt_secret", "private_key_path", "public_key_path", "flask_secret_key", "sever_side_encryption_key"]
    option_config = ["oauth"]

    def __init__(self, data):
        for key in self.required_keys:
            if key not in data:
                logging.error(f"Was expecting the key api.'{key}'")
                raise Exception(f"Was expecting the key api.'{key}'")
        for key in self.option_config:
            if key not in data:
                logging.warning(f"api.'{key}' is not set. Ignoring it ...")
        if "port" not in data:
            logging.warning(f"api.'port' is not set. Using default value: 8080")
            data["port"] = 8080
        
        try:
            self.port = int(data["port"]) 
        except:
            logging.warning("api.port is not valid. Ignoring it. Setting default value: 8080")
            self.port = 8080
        self.database_uri = data["database_uri"]
        self.jwt_secret = data["jwt_secret"]
        self.private_key_path = data["private_key_path"]
        self.public_key_path = data["public_key_path"]
        self.flask_secret_key = data["flask_secret_key"]
        self.sever_side_encryption_key = data["sever_side_encryption_key"]
        if "oauth" in data:
            self.oauth = OauthConfig(data["oauth"])
        else:
            self.oauth = None
        
class DatabaseConfig:
    required_keys = ["uri"]
    def __init__(self, data):
        for key in self.required_keys:
            if key not in data:
                logging.error(f"Was expecting the key database.'{key}'")
                raise Exception(f"Was expecting the key database.'{key}'")
        self.uri = data["uri"]

class Config:
    required_keys = ["api", "environment", "database"]
    def __init__(self, data):
        for key in self.required_keys:
            if key not in data:
                raise Exception(f"Was expecting the key '{key}'")
        self.api = APIConfig(data["api"])
        self.environment = EnvironmentConfig(data["environment"])
        self.database = DatabaseConfig(data["database"])






with open("./config/config.yml") as config_yml:
    try:
        conf = yaml.safe_load(config_yml)

    except yaml.YAMLError as exc:
        raise Exception(exc)


#port = int(os.environ.get('PORT')) if os.environ.get('PORT') != None else None
#db_uri = os.environ.get('DATABASE_URI')
#environment = os.environ.get('ENVIRONMENT')
#jwt_secret = os.environ.get('JWT_SECRET')
#private_key_path = os.environ.get('PRIVATE_KEY_PATH')
#public_key_path = os.environ.get('PUBLIC_KEY_PATH')
#oauth_client_secret_file = os.environ.get('OAUTH_CLIENT_SECRET_FILE')
#flask_secret_key = os.environ.get('FLASK_SECRET_KEY')
#sever_side_encryption_key = os.environ.get('SEVER_SIDE_ENCRYPTION_KEY')
are_all_tables_created = False
admin_can_delete_users = os.environ.get('ADMIN_CAN_DELETE_USERS') == "true"
email_sender_address = os.environ.get('EMAIL_SENDER_ADDRESS')
email_sender_password = os.environ.get('EMAIL_SENDER_PASSWORD')
email_smtp_server = os.environ.get('EMAIL_SMTP_SERVER')
email_smtp_port = os.environ.get('EMAIL_SMTP_PORT')
email_smtp_username = os.environ.get('EMAIL_SMTP_USERNAME')
require_email_validation = os.environ.get('REQUIRE_EMAIL_VALIDATION') == "true"
sentry_dsn = os.environ.get('SENTRY_DSN')
login_attempts_limit_per_ip = int(os.environ.get('LOGIN_ATTEMPTS_LIMIT_PER_IP')) if os.environ.get('LOGIN_ATTEMPTS_LIMIT_PER_IP') != None else 10
send_email_attempts_limit_per_user = int(os.environ.get('SEND_EMAIL_ATTEMPTS_LIMIT_PER_USER')) if os.environ.get('SEND_EMAIL_ATTEMPTS_LIMIT_PER_USER') != None else 5
login_ban_time = int(os.environ.get('LOGIN_BAN_TIME')) if os.environ.get('LOGIN_BAN_TIME') != None else 15
email_ban_time = int(os.environ.get('EMAIL_BAN_TIME')) if os.environ.get('EMAIL_BAN_TIME') != None else 60



if admin_can_delete_users != True:
    logging.info("ADMIN_CAN_DELETE_USERS environment variable not set. Using default value: false")
    admin_can_delete_users = False
else:
    logging.warning("ADMIN_CAN_DELETE_USERS environment variable set to true. This should be a TEMPORARY option ONLY.  Please set it to false if you are not sure what you are doing. DISABLE THIS OPTION AS SOON AS NOT NEEDED ANYMORE.")








if sever_side_encryption_key == None:
    logging.error("SEVER_SIDE_ENCRYPTION_KEY environment variable not set. Please set it to a valid secret key. Aborting...")
    raise Exception("SEVER_SIDE_ENCRYPTION_KEY environment variable not set. Please set it to a valid secret key.")


if email_sender_address == None or email_sender_password == None or email_smtp_server == None or email_smtp_port == None or email_smtp_username == None:
    logging.error("EMAIL_SENDER_ADDRESS, EMAIL_SENDER_PASSWORD, EMAIL_SMTP_SERVER, EMAIL_SMTP_USERNAME or EMAIL_SMTP_PORT environment variable not set. Email verification will not work.")

if require_email_validation == False:
    logging.info("REQUIRE_EMAIL_VALIDATION is disabled. Users will not be asked to verify their email address. You can enable this option by setting the REQUIRE_EMAIL_VALIDATION environment variable to true at any moment.")