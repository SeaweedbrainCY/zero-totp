import flask
import connexion
import json
from Utils.security_wrapper import  require_valid_user 
from database.backup_configuration_repo import BackupConfigurationRepo
from environment import conf, logging

@require_valid_user
def get_backup_configuration(user_id):
    backup_conf_repo = BackupConfigurationRepo()
    backup_conf = backup_conf_repo.get_by_user_id(user_id)
    if backup_conf is None:
        # Return default value if user has no backup configuration
        return {
            "max_age_in_days":conf.features.backup_config.max_age_in_days,
            "backup_minimum_count": conf.features.backup_config.backup_minimum_count
            }
    return {
        "max_age_in_days":int(backup_conf.backup_max_age_days),
        "backup_minimum_count":int(backup_conf.backup_minimum_count)
        },200


@require_valid_user
def get_default_backup_configuration(user_id):
    return {
        "max_age_in_days":conf.features.backup_config.max_age_in_days,
        "backup_minimum_count": conf.features.backup_config.backup_minimum_count
        },200


@require_valid_user
def set_backup_configuration(user_id, option, body):
    # Valid options:
    # - max_age_in_days
    # - backup_minimum_count
    
    backup_conf_repo = BackupConfigurationRepo()
    if option == "max_age_in_days":
        backup_conf = backup_conf_repo.set_backup_max_age_days(user_id, body["value"])
    elif option == "backup_minimum_count":
        backup_conf = backup_conf_repo.set_backup_minimum_count(user_id, body["value"])
    else: 
        return {"message": "Invalid option"}, 400
    return {
        "max_age_in_days":int(backup_conf.backup_max_age_days),
        "backup_minimum_count":int(backup_conf.backup_minimum_count)
        },200
