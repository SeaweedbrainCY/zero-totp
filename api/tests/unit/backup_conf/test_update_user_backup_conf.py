import unittest
from app import app
from database.db import db 
from zero_totp_db_model.model import User as UserModel
from unittest.mock import patch
from database.backup_configuration_repo import BackupConfigurationRepo
from database.session_token_repo import SessionTokenRepo
from environment import conf, logging

class TestUpdateUserBackupConf(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.put_backup_endpoint = "/api/v1/backup/configuration/"

        self.backup_conf_repo = BackupConfigurationRepo()
        self.session_repo = SessionTokenRepo()

        self.user1_id = 1

        self.user1 = UserModel(id=self.user1_id, username="user1", mail="user1@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role="user")

        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(self.user1)
            db.session.commit()

            _, self.session_token_user1 = self.session_repo.generate_session_token(self.user1_id)

    

    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()

    

    def test_update_user_backup_max_age_when_no_conf_yet(self):
        with self.flask_application.app.app_context():
            response = self.client.put(self.put_backup_endpoint+"max_age_in_days", json={"value": 5}, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 200)
            self.assertIn("max_age_in_days", response.json())
            self.assertEqual(response.json()["max_age_in_days"], 5)
            self.assertEqual(response.json()["backup_minimum_count"], conf.features.backup_config.backup_minimum_count)
            self.assertEqual(self.backup_conf_repo.get_by_user_id(self.user1_id).backup_max_age_days, 5)

    def test_update_user_minimum_count_when_no_conf_yet(self):
        with self.flask_application.app.app_context():
            response = self.client.put(self.put_backup_endpoint+"backup_minimum_count", json={"value": 5}, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 200)
            self.assertIn("backup_minimum_count", response.json())
            self.assertEqual(response.json()["backup_minimum_count"], 5)
            self.assertEqual(response.json()["max_age_in_days"], conf.features.backup_config.max_age_in_days)
            self.assertEqual(self.backup_conf_repo.get_by_user_id(self.user1_id).backup_minimum_count, 5)

    
    def test_update_with_bad_option(self):
        with self.flask_application.app.app_context():
            response = self.client.put(self.put_backup_endpoint+"bad_option", json={"value": 5}, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 400)
    
    def test_update_without_value(self):
        with self.flask_application.app.app_context():
            response = self.client.put(self.put_backup_endpoint+"max_age_in_days", json={"bad_body":5}, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 400)

    
    def test_update_with_non_integer_value(self):
        with self.flask_application.app.app_context():
            response = self.client.put(self.put_backup_endpoint+"max_age_in_days", json={"value":"bad_value"}, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 400)
            response = self.client.put(self.put_backup_endpoint+"backup_minimum_count", json={"value":"bad_value"}, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 400)
    
    def test_update_with_negative_value(self):
        with self.flask_application.app.app_context():
            response = self.client.put(self.put_backup_endpoint+"max_age_in_days", json={"value":-5}, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 400)
            response = self.client.put(self.put_backup_endpoint+"backup_minimum_count", json={"value":-5}, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 400)


    def test_update_with_too_big_value(self):
        with self.flask_application.app.app_context():
            response = self.client.put(self.put_backup_endpoint+"max_age_in_days", json={"value":10001}, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 400)
            response = self.client.put(self.put_backup_endpoint+"backup_minimum_count", json={"value":10001}, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 400)

    def test_update_with_too_big_value(self):
        with self.flask_application.app.app_context():
            response = self.client.put(self.put_backup_endpoint+"max_age_in_days", json={"value":10001}, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 400)
            response = self.client.put(self.put_backup_endpoint+"backup_minimum_count", json={"value":10001}, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 400)
        
            


