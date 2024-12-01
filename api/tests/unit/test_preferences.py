import unittest
from app import app
import controllers
from unittest.mock import patch
from database.user_repo import User as UserRepo
from database.preferences_repo import Preferences as PreferencesRepo
from database.session_token_repo import SessionTokenRepo
from environment import conf
import datetime
from zero_totp_db_model.model import User
from database.db import db
import base64
import json
import random

class TestPreferences(unittest.TestCase):

    minimum_backup_kept_default_value = 20
    backup_lifetime_default_value = 30
    derivation_iteration_default_value = 700000
    favicon_policy_default_value = "enabledOnly"
    autolock_delay_default_value = 10

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.client = self.application.test_client()
        self.endpoint = "/api/v1/preferences"
        self.user_id =1
        self.new_user_id = 2
        self.blocked_user_id = 3
        self.unverified_user_id = 4

        self.number_of_preferences = 5

        self.google_api_revoke_creds = patch("Oauth.google_drive_api.revoke_credentials").start()
        self.google_api_revoke_creds.return_value = True


        self.user_repo = UserRepo()
        self.preferences_repo = PreferencesRepo()
        self.session_token_repo = SessionTokenRepo()
        with self.application.app.app_context():
            db.create_all()
            self.user_repo.create(username="user1", email="user1@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now())
            self.user_repo.create(username="user2", email="user2@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now())
            self.user_repo.create(username="user3", email="user3@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now(), isBlocked=True)
            self.user_repo.create(username="user4", email="user4@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=False, today=datetime.datetime.now())
            
            self.preferences_repo.create_default_preferences(user_id=1)

            _, self.session_token_user = self.session_token_repo.generate_session_token(self.user_id)
            _, self.session_token_new_user = self.session_token_repo.generate_session_token(self.new_user_id)
            _, self.session_token_user_blocked = self.session_token_repo.generate_session_token(self.blocked_user_id)
            _, self.session_token_user_unverified = self.session_token_repo.generate_session_token(self.unverified_user_id)

            
            

    def tearDown(self):
        patch.stopall()
        with self.application.app.app_context():
            db.session.remove()
            db.drop_all()



#########
## GET ##
#########

    def test_get_all_default_pref(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["favicon_policy"], self.favicon_policy_default_value)
            self.assertEqual(response.json()["derivation_iteration"], self.derivation_iteration_default_value)
            self.assertEqual(response.json()["backup_lifetime"], self.backup_lifetime_default_value)
            self.assertEqual(response.json()["backup_minimum"], self.minimum_backup_kept_default_value)
            self.assertEqual(response.json()["autolock_delay"], self.autolock_delay_default_value)
            self.assertEqual(len(response.json()),self.number_of_preferences)
    
    def test_get_some_default_pref(self):
        with self.application.app.app_context():
            possible_value = ["favicon_policy", "derivation_iteration", "backup_lifetime", "backup_minimum","autolock_delay"]
            self.client.cookies = {'session-token': self.session_token_user}
            for i in range(10):
                random.shuffle(possible_value)
                nb_fields = random.randint(1, self.number_of_preferences)
                fields = possible_value[:nb_fields]
                response = self.client.get(self.endpoint+"?fields="+",".join(fields))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()), nb_fields)
                for field in fields:
                    self.assertIn(field, response.json())
                    if field == "favicon_policy":
                        self.assertEqual(response.json()[field], self.favicon_policy_default_value)
                    elif field == "derivation_iteration":
                        self.assertEqual(response.json()[field], self.derivation_iteration_default_value)
                    elif field == "backup_lifetime":
                        self.assertEqual(response.json()[field], self.backup_lifetime_default_value)
                    elif field == "backup_minimum":
                        self.assertEqual(response.json()[field], self.minimum_backup_kept_default_value)
                    elif field == "autolock_delay":
                        self.assertEqual(response.json()[field], self.autolock_delay_default_value)
    
    def test_get_some_default_pref_with_invalid_field(self):
        with self.application.app.app_context():
            possible_value = ["favicon_policy", "derivation_iteration", "backup_lifetime", "backup_minimum", "autolock_delay"]
            self.client.cookies = {'session-token': self.session_token_user}
            random.shuffle(possible_value)
            nb_fields = random.randint(1, self.number_of_preferences)
            fields = possible_value[:nb_fields]
            real_fields = fields.copy()
            fields.append("invalid_field")
            fields.append("all")
            response = self.client.get(self.endpoint+"?fields="+",".join(fields))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), nb_fields)
            for field in real_fields:
                self.assertIn(field, response.json())
    
    def test_get_all_modified_values(self):
        with self.application.app.app_context():
            self.preferences_repo.update_favicon(user_id=1, favicon_policy="never")
            self.preferences_repo.update_derivation_iteration(user_id=1, derivation_iteration=100000)
            self.preferences_repo.update_backup_lifetime(user_id=1, backup_lifetime=10)
            self.preferences_repo.update_minimum_backup_kept(user_id=1, minimum_backup_kept=5)
            self.preferences_repo.update_autolock_delay(user_id=1, autolock_delay=5)
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["favicon_policy"], "never")
            self.assertEqual(response.json()["derivation_iteration"], 100000)
            self.assertEqual(response.json()["backup_lifetime"], 10)
            self.assertEqual(response.json()["backup_minimum"], 5)
            self.assertEqual(response.json()["autolock_delay"], 5)
            self.assertEqual(len(response.json()), self.number_of_preferences)
    
    def test_get_invalid_fields(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.get(self.endpoint+"?fields=invalid_field,,,,,,,,")
            self.assertEqual(response.status_code, 400)

    
    def test_get_preference_new_user(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_new_user}
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["favicon_policy"], self.favicon_policy_default_value)
            self.assertEqual(response.json()["derivation_iteration"], self.derivation_iteration_default_value)
            self.assertEqual(response.json()["backup_lifetime"], self.backup_lifetime_default_value)
            self.assertEqual(response.json()["backup_minimum"], self.minimum_backup_kept_default_value)
            self.assertEqual(response.json()["autolock_delay"], self.autolock_delay_default_value)
            self.assertEqual(len(response.json()), self.number_of_preferences)
    
    def test_get_preference_blocked_user(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_blocked}
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "User is blocked")
    
    def test_get_preference_unverified_user(self):
        with self.application.app.app_context():
            print("bite", db.session.query(User).filter_by(id=4).first().isVerified )
            self.client.cookies = {'session-token': self.session_token_user_unverified}
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "Not verified")


#########
## PUT ##
#########

    def test_put_favicon_policy(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.put(self.endpoint, json={"id": "favicon_policy", "value": "never"})
            self.assertEqual(response.status_code, 201)
            preferences = self.preferences_repo.get_preferences_by_user_id(user_id=1)
            self.assertEqual(preferences.favicon_preview_policy, "never")
            self.assertEqual(preferences.derivation_iteration, self.derivation_iteration_default_value)
            self.assertEqual(preferences.backup_lifetime, self.backup_lifetime_default_value)
            self.assertEqual(preferences.minimum_backup_kept, self.minimum_backup_kept_default_value)
            response = self.client.put(self.endpoint, json={"id": "favicon_policy", "value": "always"})
            self.assertEqual(response.status_code, 201)
            preferences = self.preferences_repo.get_preferences_by_user_id(user_id=1)
            self.assertEqual(preferences.favicon_preview_policy, "always")
            self.assertEqual(preferences.derivation_iteration, self.derivation_iteration_default_value)
            self.assertEqual(preferences.backup_lifetime, self.backup_lifetime_default_value)
            self.assertEqual(preferences.minimum_backup_kept, self.minimum_backup_kept_default_value)
            response = self.client.put(self.endpoint, json={"id": "favicon_policy", "value": "enabledOnly"})
            self.assertEqual(response.status_code, 201)
            preferences = self.preferences_repo.get_preferences_by_user_id(user_id=1)
            self.assertEqual(preferences.favicon_preview_policy, "enabledOnly")
            self.assertEqual(preferences.derivation_iteration, self.derivation_iteration_default_value)
            self.assertEqual(preferences.backup_lifetime, self.backup_lifetime_default_value)
            self.assertEqual(preferences.minimum_backup_kept, self.minimum_backup_kept_default_value)
    
    def test_put_derivation_iteration(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.put(self.endpoint, json={"id": "derivation_iteration", "value": 100000})
            self.assertEqual(response.status_code, 201)
            preferences = self.preferences_repo.get_preferences_by_user_id(user_id=1)
            self.assertEqual(preferences.favicon_preview_policy, self.favicon_policy_default_value)
            self.assertEqual(preferences.derivation_iteration, 100000)
            self.assertEqual(preferences.backup_lifetime, self.backup_lifetime_default_value)
            self.assertEqual(preferences.minimum_backup_kept, self.minimum_backup_kept_default_value)

    def test_put_backup_lifetime(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.put(self.endpoint, json={"id": "backup_lifetime", "value": 10})
            self.assertEqual(response.status_code, 201)
            preferences = self.preferences_repo.get_preferences_by_user_id(user_id=1)
            self.assertEqual(preferences.favicon_preview_policy, self.favicon_policy_default_value)
            self.assertEqual(preferences.derivation_iteration, self.derivation_iteration_default_value)
            self.assertEqual(preferences.backup_lifetime, 10)
            self.assertEqual(preferences.minimum_backup_kept, self.minimum_backup_kept_default_value)
    
    def test_put_minimum_backup_kept(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.put(self.endpoint, json={"id": "backup_minimum" , "value": 10})
            self.assertEqual(response.status_code, 201)
            preferences = self.preferences_repo.get_preferences_by_user_id(user_id=1)
            self.assertEqual(preferences.favicon_preview_policy, self.favicon_policy_default_value)
            self.assertEqual(preferences.derivation_iteration, self.derivation_iteration_default_value)
            self.assertEqual(preferences.backup_lifetime, self.backup_lifetime_default_value)
            self.assertEqual(preferences.minimum_backup_kept, 10)
    
    def test_put_invalid_id(self):
         with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.put(self.endpoint, json={"id": "badId" , "value": 10})
            self.assertEqual(response.status_code, 400)
    
    def test_put_missing_value(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.put(self.endpoint, json={"id": "badId"})
            self.assertEqual(response.status_code, 400)
    
    def test_put_missing_id(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.put(self.endpoint, json={"value": "badValue"})
            self.assertEqual(response.status_code, 400)
    
    def test_mutliple_id(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.put(self.endpoint, json={"id": "backup_minimum" , "value": "10", "id": "backup_lifetime" , "value": "10"})
            self.assertEqual(response.status_code, 201)
            preferences = self.preferences_repo.get_preferences_by_user_id(user_id=1)
            self.assertEqual(preferences.favicon_preview_policy, self.favicon_policy_default_value)
            self.assertEqual(preferences.derivation_iteration, self.derivation_iteration_default_value)
            self.assertEqual(preferences.backup_lifetime, 10)
            self.assertEqual(preferences.minimum_backup_kept, self.minimum_backup_kept_default_value)
    

    
    def test_put_favicon_with_bad_value(self):
         with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.put(self.endpoint, json={"id": "favicon_policy", "value": "badValue"})
            self.assertEqual(response.status_code, 400)


    def test_put_iteration_with_bad_value(self):
         with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.put(self.endpoint, json={"id": "derivation_iteration", "value": "badValue"})
            self.assertEqual(response.status_code, 400)
            response = self.client.put(self.endpoint, json={"id": "derivation_iteration", "value": 999})
            self.assertEqual(response.status_code, 400)
            response = self.client.put(self.endpoint, json={"id": "derivation_iteration", "value": 1000001})
            self.assertEqual(response.status_code, 400)
    
    def test_put_backup_lifetime_with_bad_value(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.put(self.endpoint, json={"id": "backup_lifetime", "value": "badValue"})
            self.assertEqual(response.status_code, 400)
            response = self.client.put(self.endpoint, json={"id": "backup_lifetime", "value": 0})
            self.assertEqual(response.status_code, 400)
    
    def test_put_minimum_backup_kept_with_bad_value(self):
         with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.put(self.endpoint, json={"id": "backup_minimum", "value": "badValue"})
            self.assertEqual(response.status_code, 400)
            response = self.client.put(self.endpoint, json={"id": "backup_minimum", "value": 0})
            self.assertEqual(response.status_code, 400)

    def test_put_preference_blocked_user(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_blocked}
            response = self.client.put(self.endpoint, json={"id": "backup_minimum" , "value": "10", "id": "backup_lifetime" , "value": "10"})
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "User is blocked")
    
    def test_put_preference_unverified_user(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user_unverified}
            response = self.client.put(self.endpoint, json={"id": "backup_minimum" , "value": "10", "id": "backup_lifetime" , "value": "10"})
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "Not verified")
    
    def test_put_autolock_delay(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.put(self.endpoint, json={"id": "autolock_delay", "value": 10})
            self.assertEqual(response.status_code, 201)
            preferences = self.preferences_repo.get_preferences_by_user_id(user_id=1)
            self.assertEqual(preferences.vault_autolock_delay_min, 10)
    
    def test_put_autolock_delay_low_value(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.put(self.endpoint, json={"id": "autolock_delay", "value": 0})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()["message"], "invalid_duration")
            self.assertIsNotNone(int(response.json()["minimum_duration_min"]))

    def test_put_autolock_delay_high_value(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.put(self.endpoint, json={"id": "autolock_delay", "value": 1441})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()["message"], "invalid_duration")
            self.assertIsNotNone(int(response.json()["maximum_duration_min"]))
    
    def test_put_autolock_delay_bad_value(self):
        with self.application.app.app_context():
            self.client.cookies = {'session-token': self.session_token_user}
            response = self.client.put(self.endpoint, json={"id": "autolock_delay", "value": "badValue"})
            self.assertEqual(response.status_code, 400)