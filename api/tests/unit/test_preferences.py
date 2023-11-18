import unittest
import controllers
from app import create_app
from unittest.mock import patch
from database.user_repo import User as UserRepo
from database.preferences_repo import Preferences as PreferencesRepo
import environment as env
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
        env.db_uri = "sqlite:///:memory:"
        self.app = create_app()
        self.jwtCookie = jwt_func.generate_jwt(1)
        self.client = self.app.test_client()
        self.endpoint = "/preferences"

        self.google_api_revoke_creds = patch("Oauth.google_drive_api.revoke_credentials").start()
        self.google_api_revoke_creds.return_value = True


        self.user_repo = UserRepo()
        self.preferences_repo = PreferencesRepo()
        with self.app.app_context():
            db.create_all()
            self.user_repo.create(username="user", email="user@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now())
            self.user_repo.create(username="user", email="user@test.test", password="password", 
                    randomSalt="salt",passphraseSalt="salt", isVerified=True, today=datetime.datetime.now())
            self.preferences_repo.create_default_preferences(user_id=1)

            
            

    def tearDown(self):
        patch.stopall()
    
    def generate_expired_cookie(self):
        payload = {
            "iss": jwt_func.ISSUER,
            "sub": 1,
            "iat": datetime.datetime.utcnow(),
            "nbf": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() - datetime.timedelta(hours=1),
        }
        jwtCookie = jwt.encode(payload, env.jwt_secret, algorithm=jwt_func.ALG)
        return jwtCookie

#########
## GET ##
#########

    def test_get_all_default_pref(self):
        with self.app.app_context():
            self.client.set_cookie("localhost", "api-key", self.jwtCookie)
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["favicon_policy"], self.favicon_policy_default_value)
            self.assertEqual(response.json["derivation_iteration"], self.derivation_iteration_default_value)
            self.assertEqual(response.json["backup_lifetime"], self.backup_lifetime_default_value)
            self.assertEqual(response.json["backup_minimum"], self.minimum_backup_kept_default_value)
            self.assertEqual(len(response.json), 4)
    
    def test_get_some_default_pref(self):
        with self.app.app_context():
            possible_value = ["favicon_policy", "derivation_iteration", "backup_lifetime", "backup_minimum"]
            self.client.set_cookie("localhost", "api-key", self.jwtCookie)
            for i in range(10):
                random.shuffle(possible_value)
                nb_fields = random.randint(1, 4)
                fields = possible_value[:nb_fields]
                response = self.client.get(self.endpoint+"?fields="+",".join(fields))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json), nb_fields)
                for field in fields:
                    self.assertIn(field, response.json)
                    if field == "favicon_policy":
                        self.assertEqual(response.json[field], self.favicon_policy_default_value)
                    elif field == "derivation_iteration":
                        self.assertEqual(response.json[field], self.derivation_iteration_default_value)
                    elif field == "backup_lifetime":
                        self.assertEqual(response.json[field], self.backup_lifetime_default_value)
                    elif field == "backup_minimum":
                        self.assertEqual(response.json[field], self.minimum_backup_kept_default_value)
    
    def test_get_some_default_pref_with_invalid_field(self):
        with self.app.app_context():
            possible_value = ["favicon_policy", "derivation_iteration", "backup_lifetime", "backup_minimum"]
            self.client.set_cookie("localhost", "api-key", self.jwtCookie)
            random.shuffle(possible_value)
            nb_fields = random.randint(1, 4)
            fields = possible_value[:nb_fields]
            real_fields = fields.copy()
            fields.append("invalid_field")
            fields.append("all")
            response = self.client.get(self.endpoint+"?fields="+",".join(fields))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), nb_fields)
            for field in real_fields:
                self.assertIn(field, response.json)
    
    def test_get_all_modified_values(self):
        with self.app.app_context():
            self.preferences_repo.update_favicon(user_id=1, favicon_policy="never")
            self.preferences_repo.update_derivation_iteration(user_id=1, derivation_iteration=100000)
            self.preferences_repo.update_backup_lifetile(user_id=1, backup_lifetime=10)
            self.preferences_repo.update_minimum_backup_kept(user_id=1, minimum_backup_kept=5)
            self.client.set_cookie("localhost", "api-key", self.jwtCookie)
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["favicon_policy"], "never")
            self.assertEqual(response.json["derivation_iteration"], 100000)
            self.assertEqual(response.json["backup_lifetime"], 10)
            self.assertEqual(response.json["backup_minimum"], 5)
            self.assertEqual(len(response.json), 4)
    
    def test_get_invalid_fields(self):
        with self.app.app_context():
            self.client.set_cookie("localhost", "api-key", self.jwtCookie)
            response = self.client.get(self.endpoint+"?fields=invalid_field,,,,,,,,")
            self.assertEqual(response.status_code, 400)
    
    def test_get_pref_no_cookie(self):
        with self.app.app_context():
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 401)
    
    def test_get_pref_expired_cookie(self):
         with self.app.app_context():
            self.client.set_cookie("localhost", "api-key", self.generate_expired_cookie())
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 403)
    
    def test_get_preference_new_user(self):
        with self.app.app_context():
            self.client.set_cookie("localhost", "api-key", jwt_func.generate_jwt(2))
            response = self.client.get(self.endpoint+"?fields=all")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["favicon_policy"], self.favicon_policy_default_value)
            self.assertEqual(response.json["derivation_iteration"], self.derivation_iteration_default_value)
            self.assertEqual(response.json["backup_lifetime"], self.backup_lifetime_default_value)
            self.assertEqual(response.json["backup_minimum"], self.minimum_backup_kept_default_value)
            self.assertEqual(len(response.json), 4)