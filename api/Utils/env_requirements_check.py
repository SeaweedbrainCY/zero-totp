import re
from  CryptoClasses.serverRSAKeys import ServerRSAKeys
import logging
import ipaddress

def test_conf(conf) -> bool:
    ## API
    assert isinstance(conf.api.port, int), "api.port is not an integer"
    assert isinstance(conf.api.private_key_path, str), "api.private_key_path is not a string"
    assert isinstance(conf.api.public_key_path, str), "api.public_key_path is not a string"
    try:
        open(conf.api.private_key_path, "r").close()
        open(conf.api.public_key_path, "r").close()
    except FileNotFoundError:
        logging.info("api.private_key_path or api.public_key_path does not exist. Generating new keys ...")
        rsa_server_keys = ServerRSAKeys()
        rsa_server_keys.generate(private_key_path=conf.api.private_key_path, public_key_path=conf.api.public_key_path)
    except Exception as e:
        raise Exception(f"api.private_key_path or api.public_key_path is not a valid path. {e}")
    assert isinstance(conf.api.flask_secret_key, str), "api.flask_secret_key is not a string"
    assert len(conf.api.flask_secret_key) >= 64, "api.flask.secret_key must be at least 64 characters long"
    assert isinstance(conf.api.server_side_encryption_key, bytes), "api.server_side_encryption_key is not a string"
    if conf.api.oauth != None:
        assert isinstance(conf.api.oauth.client_secret_file_path, str), "api.oauth.client_secret_file_path is not a string"
        try:
            open(conf.api.oauth.client_secret_file_path, "r").close()
        except Exception as e:
            raise Exception(f"api.oauth.client_secret_file_path is not a valid path. {e}")
    if conf.api.trusted_proxy != None:
        assert isinstance(conf.api.trusted_proxy, list), "api.trusted_proxy is not a list"
        for ip in conf.api.trusted_proxy:
            try:
                ipaddress.ip_network(ip)
            except Exception as e:
                raise Exception(f"api.trusted_proxy contains an invalid ip address. {e}")
    
    if conf.api.session_token_validity != None:
        assert isinstance(conf.api.session_token_validity, int), "api.session_token_validity is not an integer"
        assert conf.api.session_token_validity > 0, "api.session_token_validity must be greater than 0"
    if conf.api.refresh_token_validity != None:
        assert isinstance(conf.api.refresh_token_validity, int), "api.refresh_token_validity is not an integer"
        assert conf.api.refresh_token_validity > 0, "api.refresh_token_validity must be greater than 0"

        if conf.api.session_token_validity != None:
            assert conf.api.refresh_token_validity > conf.api.session_token_validity, "api.refresh_token_validity must be greater than api.access_token"

        
    ## Environment
    assert conf.environment.type in ["local", "development", "production"], f"environment.type is not valid. Was expecting local, development or production, got {conf.environment.type}"
    if(conf.environment.type != "local"):
        assert re.match(r"^([a-z0-9|-]+\.)*[a-z0-9|-]+\.[a-z]+$", conf.environment.domain) or conf.environment.domain =="localhost" , f"environment.domain is not a valid domain. Was expecting something like 'example.com'. Got {conf.environment.domain}"

    ## Database
    assert isinstance(conf.database.database_uri, str), "database.database_uri is not a string"
    assert re.match(r"mysql:\/\/.*:.*@.*:[0-9]*\/.*", conf.database.database_uri) or conf.database.database_uri == "sqlite:///:memory:", "database.database_uri is not a valid uri. Was expecting something like 'mysql://user:password@hostname:port/dbname'"

    ## Features
    ## Emails
    assert isinstance(conf.features.emails.require_email_validation, bool), "features.emails.require_email_validation is not a boolean"
    if conf.features.emails.require_email_validation:
        assert isinstance(conf.features.emails.sender_address, str), "features.emails.sender_address is not a string"
        assert isinstance(conf.features.emails.sender_password , str), "features.emails.sender_password is not a string"
        assert isinstance(conf.features.emails.smtp_server , str), "features.emails.smtp_server is not a string"
        assert isinstance(conf.features.emails.smtp_port , int), "features.emails.smtp_port is not a integer"
        assert isinstance(conf.features.emails.smtp_username , str), "features.emails.smtp_username is not a string"
    

    ## Ratelimiting 
    assert isinstance(conf.features.rate_limiting.login_attempts_limit_per_ip, int), "features.rate_limiting.login_attempts_limit_per_ip is not an integer"
    assert isinstance(conf.features.rate_limiting.send_email_attempts_limit_per_user, int), "features.rate_limiting.send_email_attempts_limit_per_user is not an integer"
    assert isinstance(conf.features.rate_limiting.login_ban_time, int), "features.rate_limiting.login_ban_time is not an integer"
    assert isinstance(conf.features.rate_limiting.email_ban_time, int), "features.rate_limiting.email_ban_time is not an integer"

    ## Sentry
    if conf.features.sentry != None:
        assert isinstance(conf.features.sentry.dsn, str), "features.sentry.dsn is not a string"

    ## Backup
    assert isinstance(conf.features.backup_config.max_age_in_days, int), "features.default_backup_configuration.max_age_in_days is not an integer"
    assert isinstance(conf.features.backup_config.backup_minimum_count, int), "features.default_backup_configuration.backup_minimum_count is not an integer"
