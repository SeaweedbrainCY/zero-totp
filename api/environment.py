import os
import logging
import yaml 
import Utils.env_requirements_check as env_requirements_check
from CryptoClasses.serverRSAKeys import ServerRSAKeys
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512
import ipaddress

class EnvironmentConfig:
    required_keys = ["type", "config_version", "domain"]
    def __init__(self, data) -> None:
        self.config_version = data["config_version"]
        
        for key in self.required_keys:
            if key not in data:
                logging.error(f"[FATAL] Load config fail. Was expecting the key environment.{key}")
                exit(1)
        self.domain = data["domain"]
        if data["type"] == "local":
            self.type = "local"
            logging.basicConfig(
                format='%(asctime)s %(levelname)-8s %(message)s',
                level=logging.DEBUG,
                datefmt='%d-%m-%Y %H:%M:%S')
            logging.debug("Environment set to development")
            if "frontend_URI" not in data:
                logging.error("[FATAL] Load config fail. In local environement, was expecting the key environment.frontend_URI")
                exit(1)
            if "API_URI" not in data:
                logging.error("[FATAL] Load config fail. In local environement, was expecting the key environment.API_URI")
            self.frontend_URI = data["frontend_URI"]
            self.callback_URI = f'{data["API_URI"]}/api/v1/google-drive/oauth/callback'
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        elif data["type"] == "development":
            self.type = "development"
            logging.basicConfig(
                format='%(asctime)s %(levelname)-8s %(message)s',
                level=logging.INFO,
                datefmt='%d-%m-%Y %H:%M:%S')
            logging.info("Environment set to development")
            self.frontend_URI = f"https://{data['domain']}"
            self.callback_URI = f"https://{data['domain']}/api/v1/google-drive/oauth/callback"
        else:
            self.type = "production"
            logging.basicConfig(
                filename="/var/log/api/api.log",
                filemode='a',
                format='%(asctime)s %(levelname)-8s %(message)s',
                level=logging.INFO,
                datefmt='%d-%m-%Y %H:%M:%S')
            self.frontend_URI = f"https://{data['domain']}"
            self.callback_URI = f"https://{data['domain']}/api/v1/google-drive/oauth/callback"


        
class OauthConfig:
    required_keys = ["client_secret_file_path"]

    def __init__(self, data):
        for key in self.required_keys:
            if key not in data:
                logging.error(f"[FATAL] Load config fail. Was expecting the key api.oauth.{key}")
                exit(1)
        self.client_secret_file_path = data["client_secret_file_path"]

class APIConfig:
    required_keys = [ "jwt_secret", "private_key_path", "public_key_path", "flask_secret_key", "server_side_encryption_key"]
    option_config = ["oauth"]

    def __init__(self, data, config_version):
        for key in self.required_keys:
            if key not in data:
                logging.error(f"[FATAL] Load config fail. Was expecting the key api.{key}")
                exit(1)
        for key in self.option_config:
            if key not in data:
                logging.warning(f"api.{key} is not set. Ignoring it ...")
        if "port" not in data:
            logging.warning(f"api.'port' is not set. Using default value: 8080")
            data["port"] = 8080
        
        try:
            self.port = int(data["port"]) 
        except:
            logging.warning("api.port is not valid. Ignoring it. Setting default value: 8080")
            self.port = 8080
        
        self.jwt_secret = data["jwt_secret"]            
        self.private_key_path = data["private_key_path"]
        self.public_key_path = data["public_key_path"]
        self.flask_secret_key = data["flask_secret_key"]
        try:
            if config_version >= 1.0:
                self.server_side_encryption_key = PBKDF2(data["server_side_encryption_key"].encode("utf-8"), '4ATK7mA8aKgT6768' , count=2000000, dkLen=32, hmac_hash_module=SHA512)
            else:
                logging.error(f"[FATAL] Load config fail. config version {config_version} is not supported.")
                exit(1)
        except Exception as e:
            logging.error(f"[FATAL] Load config fail. {e}")
            exit(1)
        if "oauth" in data:
            self.oauth = OauthConfig(data["oauth"])
        else:
            self.oauth = None

        self.trusted_proxy = None
        if "trusted_proxy" in data:
            self.trusted_proxy = []
            for ip in data["trusted_proxy"]:
                try:
                    self.trusted_proxy.append(ipaddress.ip_network(ip))
                except Exception as e:
                    logging.error(f"[FATAL] Load config fail. api.trusted_proxy contains an invalid ip address. {e}")
                    exit(1)
        self.access_token_validity = 3600
        if "access_token_validity" in data:
            try:
                self.access_token_validity = int(data["access_token_validity"])
            except Exception as e:
                logging.error(f"[FATAL] Load config fail. api.access_token_validity is not valid. {e}")
                exit(1)
        
        self.refresh_token_validity = 86400
        if "refresh_token_validity" in data:
            try:
                self.refresh_token_validity = int(data["refresh_token_validity"])
            except Exception as e:
                logging.error(f"[FATAL] Load config fail. api.refresh_token_validity is not valid. {e}")
                exit(1)
                
        
class DatabaseConfig:
    required_keys = ["database_uri"]
    def __init__(self, data):
        for key in self.required_keys:
            if key not in data:
                logging.error(f"[FATAL] Load config fail. Was expecting the key database.{key}")
                exit(1)
        self.database_uri = data["database_uri"]
        self.are_all_tables_created = False

class AdminsConfig:
    def __init__(self, data):
        if "admin_can_delete_users" not in data:
            logging.info("ADMIN_CAN_DELETE_USERS environment variable not set. Using default value: false")
            self.admin_can_delete_users = False
        else:
            
            try: 
                self.admin_can_delete_users = bool(data["admin_can_delete_users"])
            except Exception as e:
                logging.error(f"[FATAL] Load config fail. {e}")
                exit(1)
            if self.admin_can_delete_users:
                logging.warning("ADMIN_CAN_DELETE_USERS environment variable set to true. This should be a TEMPORARY option ONLY.  Please set it to false if you are not sure what you are doing. DISABLE THIS OPTION AS SOON AS NOT NEEDED ANYMORE.")


class EmailsConfig:
    required_keys = ["email_sender_address", "email_smtp_password", "email_smtp_server", "email_smtp_port", "email_smtp_username"]
    def __init__(self, data):
        if "require_email_validation" not in data:
            data["require_email_validation"] = False
        if data["require_email_validation"] == False:
            logging.warning("require_email_validation is disabled. Users will not be asked to verify their email address. You can enable this option by setting the require_email_validation  variable to true at any moment.")
            self.require_email_validation = False
        else :
            self.require_email_validation = True
            for key in self.required_keys:
                if key not in data:
                    logging.error(f"[FATAL] Load config fail. Was expecting the key features.emails.{key} because require_email_validation is set to true")
                    exit(1)
            self.sender_address = data["email_sender_address"]
            self.sender_password = data["email_smtp_password"]
            self.smtp_server = data["email_smtp_server"]
            self.smtp_port = data["email_smtp_port"]
            self.smtp_username = data["email_smtp_username"]

class RateLimitingConfig:
    def __init__(self, data):
        try :
            self.login_attempts_limit_per_ip = int(data["login_attempts_limit_per_ip"]) if "login_attempts_limit_per_ip" in data else 10
            self.send_email_attempts_limit_per_user = int(data["send_email_attempts_limit_per_user"]) if "send_email_attempts_limit_per_user" in data else 5
            self.login_ban_time = int(data["login_ban_time"]) if "login_ban_time" in data else 15
            self.email_ban_time = int(data["email_ban_time"]) if "email_ban_time" in data else 60
        except Exception as e:
            logging.error(f"[FATAL] Load config fail. {e}")
            exit(1)


class SentryConfig:
    required_keys = ["dsn"]
    def __init__(self, data):
        for key in self.required_keys:
            if key not in data:
                logging.error(f"[FATAL] Load config fail. Was expecting the key features.sentry.{key}")
                exit(1)
        self.dsn = data["dsn"]


class FeaturesConfig:
    def __init__(self, data):
                
        self.admins = AdminsConfig(data["admins"] if "admins" in data else [])
        self.emails = EmailsConfig(data["emails"]) if "emails" in data else None
        self.rate_limiting = RateLimitingConfig(data["rate_limiting"] if "rate_limiting" in data else [])
        self.sentry = SentryConfig(data["sentry"]) if "sentry" in data else None


class Config:
    required_keys = ["api", "environment", "database", "features"]
    def __init__(self, data):
        for key in self.required_keys:
            if key not in data:
                logging.error(f"[FATAL] Load config fail. Was expecting the key {key}")
                exit(1)
        self.environment = EnvironmentConfig(data["environment"] if data["environment"] != None else [])
        self.api = APIConfig(data["api"] if data["api"] != None else [], self.environment.config_version)
        self.database = DatabaseConfig(data["database"] if data["database"] != None else [])
        self.features = FeaturesConfig(data["features"] if data["features"] != None else [])




try:
    with open("./config/config.yml") as config_yml:
        try:
            raw_conf = yaml.safe_load(config_yml)
            conf = Config(raw_conf)
        
        except yaml.YAMLError as exc:
            raise Exception(exc)
except Exception as e :
    logging.error(f"[FATAL] API will stop now. Error while checking /api/config/config.yml, {e}")
    exit(1)


env_requirements_check.test_conf(conf) 