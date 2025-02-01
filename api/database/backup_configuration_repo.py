from database.db import db 
from zero_totp_db_model.model import BackupConfiguration as Backup_Configuration_model
from environment import conf

class BackupConfigurationRepo:
    def get_by_user_id(self, user_id) -> Backup_Configuration_model|None:
        return db.session.query(Backup_Configuration_model).filter_by(user_id=user_id).first()

    def create_default_backup_configuration(self, user_id) -> Backup_Configuration_model:
        backup_conf = Backup_Configuration_model(user_id=user_id, backup_max_age_days=conf.features.backup_config.max_age_in_days, backup_minimum_count=conf.features.backup_config.backup_minimum_count)
        db.session.add(backup_conf)
        db.session.commit()
        return backup_conf

    
    def set_backup_max_age_days(self, user_id, max_age_in_days) -> Backup_Configuration_model:
        backup_conf = self.get_by_user_id(user_id)
        if backup_conf is None:
            backup_conf = self.create_default_backup_configuration(user_id)
        backup_conf.backup_max_age_days = max_age_in_days
        db.session.add(backup_conf)
        db.session.commit()
        return backup_conf

    
    def set_backup_minimum_count(self, user_id, backup_minimum_count)-> Backup_Configuration_model:
        backup_conf = self.get_by_user_id(user_id)
        if backup_conf is None:
            backup_conf = self.create_default_backup_configuration(user_id)
        backup_conf.backup_minimum_count = backup_minimum_count
        db.session.add(backup_conf)
        db.session.commit()
        return backup_conf
    