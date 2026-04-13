import unittest
from app import app 
from environment import conf
from uuid import uuid4
from database.db import db 
from database.user_repo import User as UserRepo
from database.totp_secret_repo import TOTP_secret as TOTPRepo
import datetime
from Utils import utils



class TestEncryptedSecretsController(unittest.TestCase):
    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/encrypted_secrets"
        self.secret_ids = [str(uuid4()) for _ in range(3)]
        self.secret_id_user2 = str(uuid4())
        
        self.user_repo = UserRepo()
        self.totp_secret_repo = TOTPRepo()

        with self.flask_application.app.app_context():
            db.create_all()
            user = self.user_repo.create(username='user1', email='user1@test.com', password='test', randomSalt='salt', passphraseSalt='salt', today=datetime.datetime.now(), isVerified=True)
            self.user_id = user.id
            user2 = self.user_repo.create(username='user2', email='user2@test.com', password='test', randomSalt='salt', passphraseSalt='salt', today=datetime.datetime.now(), isVerified=True)
            self.user_id2 = user2.id

            for secret_id in self.secret_ids:
                self.totp_secret_repo.add(user_id=self.user_id, enc_secret="secret", uuid=secret_id)
            self.totp_secret_repo.add(user_id=self.user_id2, enc_secret="secret", uuid=self.secret_id_user2)
            db.session.commit()

            self.session_token, _ = utils.generate_new_session(user=user, ip_address=None)


        # We mock encrypted data with uuid.
        self.json_payload = {"encrypted_secrets_list": [str(uuid4()) for _ in range(10)]}



    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_post_encrypted_secrets(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.post(self.endpoint, json=self.json_payload)
            self.assertEqual(response.status_code, 201)
            self.assertIn("uuid_list", response.json().keys())
            self.assertIn("message", response.json().keys())
            self.assertEqual(response.json()["message"], "OK")
            self.assertEqual(len(self.json_payload["encrypted_secrets_list"]), len(response.json()["uuid_list"]))

            for uuid in response.json()["uuid_list"]:
                secret = self.totp_secret_repo.get_enc_secret_by_uuid(uuid)
                self.assertIn(secret.secret_enc, self.json_payload["encrypted_secrets_list"])
    
    def test_post_0_encrypted_secrets(self):
        payload = self.json_payload.copy()
        payload["encrypted_secrets_list"] = []
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.post(self.endpoint, json=payload)
            self.assertEqual(response.status_code, 201)
            self.assertIn("uuid_list", response.json().keys())
            self.assertIn("message", response.json().keys())
            self.assertEqual(response.json()["message"], "OK")
            self.assertEqual(0, len(response.json()["uuid_list"]))

    def test_post_101_encrypted_secrets(self):
        # 100 is the maximum limit for imported secrets
        payload = self.json_payload.copy()
        payload["encrypted_secrets_list"] = [str(uuid4()) for _ in range(101)]
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.post(self.endpoint, json=payload)
            self.assertEqual(response.status_code, 400)
            self.assertIn("message", response.json().keys())
            self.assertEqual(response.json()["message"], "The number of maximum encrypted secrets submitted is over the limit.")