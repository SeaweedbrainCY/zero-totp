from database.db import db 
from database.model import GoogleDriveIntegration as GoogleDriveIntegrationModel
from environment import logging

class GoogleDriveIntegration:
    

    def is_google_drive_enabled(self, user_id):
        integration = db.session.query(GoogleDriveIntegrationModel).filter_by(user_id=user_id).first()
        if integration == None:
             return False
        return integration.isEnabled
    
    def update_google_drive_sync(self, user_id, google_drive_sync):
        integration = db.session.query(GoogleDriveIntegrationModel).filter_by(user_id=user_id).first()
        if integration == None:
            self.create(user_id, google_drive_sync)
        integration.isEnabled = google_drive_sync
        db.session.commit()
        return integration
    
    def update_last_backup_clean_date(self, user_id, last_backup_clean_date):
        integration = db.session.query(GoogleDriveIntegrationModel).filter_by(user_id=user_id).first()
        if integration == None:
            return None
        integration.lastBackupCleanDate = last_backup_clean_date
        db.session.commit()
        return integration
    
    def get_last_backup_clean_date(self, user_id):
        integration = db.session.query(GoogleDriveIntegrationModel).filter_by(user_id=user_id).first()
        if integration == None:
            return None
        return integration.lastBackupCleanDate

    def get_by_user_id(self, user_id):
        return db.session.query(GoogleDriveIntegrationModel).filter_by(user_id=user_id).first()
    
    def create(self, user_id, google_drive_sync):
        integration = GoogleDriveIntegrationModel(user_id=user_id)
        integration.isEnabled = google_drive_sync
        db.session.add(integration)
        db.session.commit()
        return integration
    
    def delete(self, user_id):
        db.session.query(GoogleDriveIntegrationModel).filter_by(user_id=user_id).delete()
        db.session.commit()
        return True
