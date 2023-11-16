from database.db import db 
from database.model import Preferences as PreferencesModel
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

    