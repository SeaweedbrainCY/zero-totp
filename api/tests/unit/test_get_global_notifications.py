import unittest
from app import app
from database.db import db 
from environment import conf
from zero_totp_db_model import model
from unittest.mock import patch
import datetime
from uuid import uuid4


class TestGetGlobalNotification(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/notification/global"
    
       
    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()

    
    def test_get_notification(self):
        notif = model.Notifications(id=str(uuid4()), message="message", timestamp=datetime.datetime.now(datetime.UTC).timestamp())
        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(notif)
            db.session.commit()
        with self.flask_application.app.app_context():
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["display_notification"], True)
            self.assertEqual(response.json()["message"], "message")
            self.assertIn("timestamp", response.json())
    
    def test_get_last_notification(self):
        notif_old = model.Notifications(id=str(uuid4()), message="old", timestamp=datetime.datetime.now(datetime.UTC).timestamp())
        notif_new = model.Notifications(id=str(uuid4()), message="new", timestamp=datetime.datetime.now(datetime.UTC).timestamp())
        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(notif_old)
            db.session.add(notif_new)
            db.session.commit()
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["display_notification"], True)
            self.assertEqual(response.json()["message"], "new")
            self.assertIn("timestamp", response.json())
    
    def test_get_last_enabled_notification(self):
        notif_old = model.Notifications(id=str(uuid4()), message="old", timestamp=datetime.datetime.now(datetime.UTC).timestamp())
        notif_new = model.Notifications(id=str(uuid4()), message="new", timestamp=datetime.datetime.now(datetime.UTC).timestamp(), enabled=False)
        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(notif_old)
            db.session.add(notif_new)
            db.session.commit()
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["display_notification"], True)
            self.assertEqual(response.json()["message"], "old")
            self.assertIn("timestamp", response.json())
    
    def test_get_last_not_expired_notification(self):
        notif_old = model.Notifications(id=str(uuid4()), message="old", timestamp=datetime.datetime.now(datetime.UTC).timestamp())
        notif_new = model.Notifications(id=str(uuid4()), message="new", timestamp=datetime.datetime.now(datetime.UTC).timestamp(), expiry=str((datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)).timestamp()))
        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(notif_old)
            db.session.add(notif_new)
            db.session.commit()
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["display_notification"], True)
            self.assertEqual(response.json()["message"], "old")
            self.assertIn("timestamp", response.json())
    
    def test_get_no_notification(self):
        with self.flask_application.app.app_context():
            db.create_all()
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["display_notification"], False)
    
    def test_get_notification_for_auth_only(self):
        notif = model.Notifications(id=str(uuid4()), message="message", timestamp=datetime.datetime.now(datetime.UTC).timestamp(), authenticated_user_only=True)
        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(notif)
            db.session.commit()
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["display_notification"], True)
            self.assertEqual(response.json()["authenticated_user_only"], True)
    
    def test_all_expired_notification(self):
        notif_old = model.Notifications(id=str(uuid4()), message="old", timestamp=datetime.datetime.now(datetime.UTC).timestamp(), expiry=str((datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)).timestamp()))
        notif_new = model.Notifications(id=str(uuid4()), message="new", timestamp=datetime.datetime.now(datetime.UTC).timestamp(), expiry=str((datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)).timestamp()))
        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(notif_old)
            db.session.add(notif_new)
            db.session.commit()
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["display_notification"], False)
    
    


    


