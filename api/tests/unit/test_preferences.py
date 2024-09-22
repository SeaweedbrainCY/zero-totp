import unittest
from app import app
import controllers
from unittest.mock import patch
from database.user_repo import User as UserRepo
from database.preferences_repo import Preferences as PreferencesRepo
from environment import conf
from CryptoClasses import jwt_func
import jwt
import datetime
from database.db import db
import base64
import json
import random

class TestPreferences(unittest.TestCase):

    minimum_backup_kept_default_value = 20
    backup_lifetime_default_value = 30
    derivation_iteration_default_value = 700000
    favicon_policy_default_value = "enabledOnly"

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.application.test_client()
        self.endpoint = "/api/v1/preferences"
        self.user_id =1
        self.new_user_id = 2
        self.blocked_user_id = 3
        self.unverified_user_id = 4

        self.google_api_revoke_creds = patch("Oauth.google_drive_api.revoke_credentials").start()
        self.google_api_revoke_creds.return_value = True


        self.user_repo = UserRepo()
        self.preferences_repo = PreferencesRepo()
        with self.application.app.app_context():
            db.create_all()
            self.user_repo.create(username="user", email="user@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now())
            self.user_repo.create(username="user", email="user@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now())
            self.user_repo.create(username="user", email="user@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now(), isBlocked=True)
            self.user_repo.create(username="user", email="user@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=False, today=datetime.datetime.now())
            
            self.preferences_repo.create_default_preferences(user_id=1)

            
            

    def tearDown(self):
        patch.stopall()
        with self.application.app.app_context():
            db.session.remove()
            db.drop_all()

    
    def generate_expired_cookie(self):
        payload = {
            "iss": jwt_func.ISSUER,
            "sub": 1,
            "iat": datetime.datetime.utcnow(),
            "nbf": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() - datetime.timedelta(hours=1),
        }
        jwtCookie = jwt.encode(payload,conf.api.jwt_secret, algorithm=jwt_func.ALG)
        return jwtCookie

#########
## GET ##
#########

    def test_get_all_default_pref(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["favicon_policy"], self.favicon_policy_default_value)
            self.assertEqual(response.json()["derivation_iteration"], self.derivation_iteration_default_value)
            self.assertEqual(response.json()["backup_lifetime"], self.backup_lifetime_default_value)
            self.assertEqual(response.json()["backup_minimum"], self.minimum_backup_kept_default_value)
            self.assertEqual(len(response.json()), 4)
    
    def test_get_some_default_pref(self):
        with self.application.app.app_context():
            possible_value = ["favicon_policy", "derivation_iteration", "backup_lifetime", "backup_minimum"]
            self.client.cookies = {"api-key": self.jwtCookie}
            for i in range(10):
                random.shuffle(possible_value)
                nb_fields = random.randint(1, 4)
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
    
    def test_get_some_default_pref_with_invalid_field(self):
        with self.application.app.app_context():
            possible_value = ["favicon_policy", "derivation_iteration", "backup_lifetime", "backup_minimum"]
            self.client.cookies = {"api-key": self.jwtCookie}
            random.shuffle(possible_value)
            nb_fields = random.randint(1, 4)
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
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["favicon_policy"], "never")
            self.assertEqual(response.json()["derivation_iteration"], 100000)
            self.assertEqual(response.json()["backup_lifetime"], 10)
            self.assertEqual(response.json()["backup_minimum"], 5)
            self.assertEqual(len(response.json()), 4)
    
    def test_get_invalid_fields(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.get(self.endpoint+"?fields=invalid_field,,,,,,,,")
            self.assertEqual(response.status_code, 400)
    
    def test_get_pref_no_cookie(self):
        with self.application.app.app_context():
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 401)
    
    def test_get_pref_expired_cookie(self):
         with self.application.app.app_context():
            self.client.cookies = {"api-key": self.generate_expired_cookie()}
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 403)
    
    def test_get_preference_new_user(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": jwt_func.generate_jwt(self.new_user_id)}
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["favicon_policy"], self.favicon_policy_default_value)
            self.assertEqual(response.json()["derivation_iteration"], self.derivation_iteration_default_value)
            self.assertEqual(response.json()["backup_lifetime"], self.backup_lifetime_default_value)
            self.assertEqual(response.json()["backup_minimum"], self.minimum_backup_kept_default_value)
            self.assertEqual(len(response.json()), 4)
    
    def test_get_preference_blocked_user(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": jwt_func.generate_jwt(self.blocked_user_id)}
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["message"], "User is blocked")
    
    def test_get_preference_unverified_user(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": jwt_func.generate_jwt(self.unverified_user_id)}
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["message"], "Not verified")


##########
## POST ##
##########

    def test_put_favicon_policy(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
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
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.put(self.endpoint, json={"id": "derivation_iteration", "value": 100000})
            self.assertEqual(response.status_code, 201)
            preferences = self.preferences_repo.get_preferences_by_user_id(user_id=1)
            self.assertEqual(preferences.favicon_preview_policy, self.favicon_policy_default_value)
            self.assertEqual(preferences.derivation_iteration, 100000)
            self.assertEqual(preferences.backup_lifetime, self.backup_lifetime_default_value)
            self.assertEqual(preferences.minimum_backup_kept, self.minimum_backup_kept_default_value)

    def test_put_backup_lifetime(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.put(self.endpoint, json={"id": "backup_lifetime", "value": 10})
            print(response.json())
            self.assertEqual(response.status_code, 201)
            preferences = self.preferences_repo.get_preferences_by_user_id(user_id=1)
            self.assertEqual(preferences.favicon_preview_policy, self.favicon_policy_default_value)
            self.assertEqual(preferences.derivation_iteration, self.derivation_iteration_default_value)
            self.assertEqual(preferences.backup_lifetime, 10)
            self.assertEqual(preferences.minimum_backup_kept, self.minimum_backup_kept_default_value)
    
    def test_put_minimum_backup_kept(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.put(self.endpoint, json={"id": "backup_minimum" , "value": 10})
            self.assertEqual(response.status_code, 201)
            preferences = self.preferences_repo.get_preferences_by_user_id(user_id=1)
            self.assertEqual(preferences.favicon_preview_policy, self.favicon_policy_default_value)
            self.assertEqual(preferences.derivation_iteration, self.derivation_iteration_default_value)
            self.assertEqual(preferences.backup_lifetime, self.backup_lifetime_default_value)
            self.assertEqual(preferences.minimum_backup_kept, 10)
    
    def test_put_invalid_id(self):
         with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.put(self.endpoint, json={"id": "badId" , "value": 10})
            self.assertEqual(response.status_code, 400)
    
    def test_put_missing_value(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.put(self.endpoint, json={"id": "badId"})
            self.assertEqual(response.status_code, 400)
    
    def test_put_missing_id(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.put(self.endpoint, json={"value": "badValue"})
            self.assertEqual(response.status_code, 400)
    
    def test_mutliple_id(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.put(self.endpoint, json={"id": "backup_minimum" , "value": "10", "id": "backup_lifetime" , "value": "10"})
            self.assertEqual(response.status_code, 201)
            preferences = self.preferences_repo.get_preferences_by_user_id(user_id=1)
            self.assertEqual(preferences.favicon_preview_policy, self.favicon_policy_default_value)
            self.assertEqual(preferences.derivation_iteration, self.derivation_iteration_default_value)
            self.assertEqual(preferences.backup_lifetime, 10)
            self.assertEqual(preferences.minimum_backup_kept, self.minimum_backup_kept_default_value)
    

    
    def test_put_favicon_with_bad_value(self):
         with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.put(self.endpoint, json={"id": "favicon_policy", "value": "badValue"})
            self.assertEqual(response.status_code, 400)


    def test_put_iteration_with_bad_value(self):
         with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.put(self.endpoint, json={"id": "derivation_iteration", "value": "badValue"})
            self.assertEqual(response.status_code, 400)
            response = self.client.put(self.endpoint, json={"id": "derivation_iteration", "value": 999})
            self.assertEqual(response.status_code, 400)
            response = self.client.put(self.endpoint, json={"id": "derivation_iteration", "value": 1000001})
            self.assertEqual(response.status_code, 400)
    
    def test_put_backup_lifetime_with_bad_value(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.put(self.endpoint, json={"id": "backup_lifetime", "value": "badValue"})
            self.assertEqual(response.status_code, 400)
            response = self.client.put(self.endpoint, json={"id": "backup_lifetime", "value": 0})
            self.assertEqual(response.status_code, 400)
    
    def test_put_minimum_backup_kept_with_bad_value(self):
         with self.application.app.app_context():
            self.client.cookies = {"api-key": self.jwtCookie}
            response = self.client.put(self.endpoint, json={"id": "backup_minimum", "value": "badValue"})
            self.assertEqual(response.status_code, 400)
            response = self.client.put(self.endpoint, json={"id": "backup_minimum", "value": 0})
            self.assertEqual(response.status_code, 400)

    def test_get_preference_blocked_user(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": jwt_func.generate_jwt(self.blocked_user_id)}
            response = self.client.put(self.endpoint, json={"id": "backup_minimum" , "value": "10", "id": "backup_lifetime" , "value": "10"})
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "User is blocked")
    
    def test_get_preference_unverified_user(self):
        with self.application.app.app_context():
            self.client.cookies = {"api-key": jwt_func.generate_jwt(self.unverified_user_id)}
            response = self.client.put(self.endpoint, json={"id": "backup_minimum" , "value": "10", "id": "backup_lifetime" , "value": "10"})
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "Not verified")