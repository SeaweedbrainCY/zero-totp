import unittest
from app import app
from database.db import db 
from zero_totp_db_model.model import User as UserModel
from unittest.mock import patch
from database.backup_configuration_repo import BackupConfigurationRepo
from environment import conf
from Utils import utils


class TestGetBackupServerOption(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.get_backup_endpoint = "/api/v1/backup/server/options"

        self.user1_id = 1

        user1 = UserModel(id=self.user1_id, username="user1", mail="user1@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role="user")

        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(user1)
            db.session.commit()

            self.session_token_user1, _ = utils.generate_new_session(user=user1, ip_address=None)
    

    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()


    def test_get_backup_server_options(self):
        with self.flask_application.app.app_context():
            response = self.client.get(self.get_backup_endpoint, cookies={"session-token": self.session_token_user1})
            self.assertEqual(response.status_code, 200)
            self.assertIn("google_drive_enabled", response.json())
            self.assertIsInstance(response.json()["google_drive_enabled"], bool)
            self.assertEqual(response.json()["google_drive_enabled"], conf.features.google_drive.enabled)

    def test_get_backup_server_options_enabled(self):
        with self.flask_application.app.app_context():
            with patch.object(conf.features.google_drive, 'enabled', True):
                response = self.client.get(self.get_backup_endpoint, cookies={"session-token": self.session_token_user1})
                self.assertEqual(response.status_code, 200)
                self.assertIn("google_drive_enabled", response.json())
                self.assertTrue(response.json()["google_drive_enabled"])
    
    def test_get_backup_server_options_disabled(self):
        with self.flask_application.app.app_context():
            with patch.object(conf.features.google_drive, 'enabled', False):
                response = self.client.get(self.get_backup_endpoint, cookies={"session-token": self.session_token_user1})
                self.assertEqual(response.status_code, 200)
                self.assertIn("google_drive_enabled", response.json())
                self.assertFalse(response.json()["google_drive_enabled"])

