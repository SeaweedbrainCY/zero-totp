import unittest
from app import app
from database.db import db 
from zero_totp_db_model.model import User as UserModel
from unittest.mock import patch
from database.backup_configuration_repo import BackupConfigurationRepo
from database.session_token_repo import SessionTokenRepo
from environment import conf

class TestGetServerDefaultBackupConf(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.get_backup_endpoint = "/api/v1/backup/default/configuration"

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

    

    def test_get_server_default_backup_conf_with_saved_conf_for_user(self):
        with self.flask_application.app.app_context():
            self.backup_conf_repo.set_backup_max_age_days(self.user1_id, 10)
            self.backup_conf_repo.set_backup_minimum_count(self.user1_id, 5)

            response = self.client.get(self.get_backup_endpoint, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 200)
            self.assertIn("max_age_in_days", response.json())
            self.assertIn("backup_minimum_count", response.json())
            self.assertEqual(response.json()["max_age_in_days"], conf.features.backup_config.max_age_in_days)
            self.assertEqual(response.json()["backup_minimum_count"], conf.features.backup_config.backup_minimum_count)

    def test_get_server_default_backup_conf_when_no_conf_yet(self):
        with self.flask_application.app.app_context():
            response = self.client.get(self.get_backup_endpoint, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 200)
            self.assertIn("max_age_in_days", response.json())
            self.assertIn("backup_minimum_count", response.json())
            self.assertEqual(response.json()["max_age_in_days"], conf.features.backup_config.max_age_in_days)
            self.assertEqual(response.json()["backup_minimum_count"], conf.features.backup_config.backup_minimum_count)

    def test_get_server_default_backup_conf_only_max_age_set(self):
        with self.flask_application.app.app_context():
            self.backup_conf_repo.set_backup_max_age_days(self.user1_id, 10)

            response = self.client.get(self.get_backup_endpoint, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 200)
            self.assertIn("max_age_in_days", response.json())
            self.assertIn("backup_minimum_count", response.json())
            self.assertEqual(response.json()["max_age_in_days"], conf.features.backup_config.max_age_in_days)
            self.assertEqual(response.json()["backup_minimum_count"], conf.features.backup_config.backup_minimum_count)


    def test_get_user_backup_conf_only_minimum_count_set(self):
        with self.flask_application.app.app_context():
            self.backup_conf_repo.set_backup_minimum_count(self.user1_id, 10)

            response = self.client.get(self.get_backup_endpoint, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 200)
            self.assertIn("max_age_in_days", response.json())
            self.assertIn("backup_minimum_count", response.json())
            self.assertEqual(response.json()["max_age_in_days"], conf.features.backup_config.max_age_in_days)
            self.assertEqual(response.json()["backup_minimum_count"], conf.features.backup_config.backup_minimum_count)
            


