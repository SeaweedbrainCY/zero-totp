import flask
import connexion
import json
from Utils.security_wrapper import  require_valid_user 
from database.backup_configuration_repo import BackupConfigurationRepo
from environment import conf, logging

@require_valid_user
def get_backup_configuration(user_id, dv=None):
    backup_conf_repo = BackupConfigurationRepo()
    backup_conf = backup_conf_repo.get_by_user_id(user_id)
    body = {}
    if dv == "true":
        body = {
            "default_max_age_in_days":conf.features.backup_config.max_age_in_days,
            "default_backup_minimum_count": conf.features.backup_config.backup_minimum_count
            }
    if backup_conf is None:
        # Return default value if user has no backup configuration
        body["max_age_in_days"] = conf.features.backup_config.max_age_in_days
        body["backup_minimum_count"] = conf.features.backup_config.backup_minimum_count
    else:
        body["max_age_in_days"] = int(backup_conf.backup_max_age_days)
        body["backup_minimum_count"] = int(backup_conf.backup_minimum_count)
    return body,200





@require_valid_user
def set_backup_configuration(user_id, option, body):
    # Valid options:
    # - max_age_in_days
    # - backup_minimum_count

    unsecure_value = body["value"]
    try :
        value = int(unsecure_value)
    except Exception as e:
        logging.warning(f"The user {user_id} tried to set a non integer value for the backup configuration. Value: {unsecure_value}. Error: {e}")
        return {"message": "Invalid value"}, 400

    if value < 0:
        return {"message": "Invalid value"}, 400
    
    if value > 10000:
        return {"message": "Invalid value"}, 400
    
    backup_conf_repo = BackupConfigurationRepo()
    if option == "max_age_in_days":
        backup_conf = backup_conf_repo.set_backup_max_age_days(user_id, value)
    elif option == "backup_minimum_count":
        backup_conf = backup_conf_repo.set_backup_minimum_count(user_id,value)
    else: 
        return {"message": "Invalid option"}, 400
    return {
        "max_age_in_days":int(backup_conf.backup_max_age_days),
        "backup_minimum_count":int(backup_conf.backup_minimum_count)
        },200
