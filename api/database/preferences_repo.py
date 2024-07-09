from database.db import db 
from zero_totp_db_model.model import Preferences as PreferencesModel
from environment import logging

class Preferences:


    def create_default_preferences(self, user_id):
        pref = PreferencesModel(user_id=user_id)
        db.session.add(pref)
        db.session.commit()
        return pref

    def get_preferences_by_user_id(self, user_id):
        pref = db.session.query(PreferencesModel).filter_by(user_id=user_id).first()
        if pref == None:
            pref = self.create_default_preferences(user_id)
        return pref
    
    def update_favicon(self, user_id, favicon_policy):
        pref = db.session.query(PreferencesModel).filter_by(user_id=user_id).first()
        if pref == None:
            pref = self.create_default_preferences(user_id)
        pref.favicon_preview_policy = favicon_policy
        db.session.commit()
        return pref
    
    def update_derivation_iteration(self, user_id, derivation_iteration):
        pref = db.session.query(PreferencesModel).filter_by(user_id=user_id).first()
        if pref == None:
            pref = self.create_default_preferences(user_id)
        pref.derivation_iteration = derivation_iteration
        db.session.commit()
        return pref
    
    def update_minimum_backup_kept(self, user_id, minimum_backup_kept):
        pref = db.session.query(PreferencesModel).filter_by(user_id=user_id).first()
        if pref == None:
            pref = self.create_default_preferences(user_id)
        pref.minimum_backup_kept = minimum_backup_kept
        db.session.commit()
        return pref
    
    def update_backup_lifetime(self, user_id, backup_lifetime):
        pref = db.session.query(PreferencesModel).filter_by(user_id=user_id).first()
        if pref == None:
            pref = self.create_default_preferences(user_id)
        pref.backup_lifetime = backup_lifetime
        db.session.commit()
        return pref
    
    def delete(self, user_id):
        db.session.query(PreferencesModel).filter_by(user_id=user_id).delete()
        db.session.commit()
        return True

    