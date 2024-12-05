import unittest
from app import app
from database.db import db 
import controllers
from unittest.mock import patch
from zero_totp_db_model.model import User, TOTP_secret, ZKE_encryption_key
from environment import conf
from CryptoClasses.sign_func import API_signature
from database.user_repo import User as UserRepo
from database.totp_secret_repo import TOTP_secret as TOTPRepo
from database.session_token_repo import SessionTokenRepo
from database.zke_repo import ZKE as ZKERepo
import datetime
import base64
import json
from uuid import uuid4

class TestAllSecret(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/vault/export"

        self.secret_ids = [str(uuid4()) for _ in range(3)]
        self.secret_id_user2 = str(uuid4())

        self.user_repo = UserRepo()
        self.totp_secret_repo = TOTPRepo()
        self.session_repo = SessionTokenRepo()
        self.zke_repo = ZKERepo()

        with self.flask_application.app.app_context():
            db.create_all()
            user = self.user_repo.create(username='user1', email='user1@test.com', password='test', randomSalt='salt', passphraseSalt='salt', today=datetime.datetime.now(), isVerified=True)
            self.zke_repo.create(user_id=user.id, encrypted_key="key")
            self.user_id = user.id
            user2 = self.user_repo.create(username='user2', email='user2@test.com', password='test', randomSalt='salt', passphraseSalt='salt', today=datetime.datetime.now(), isVerified=True)
            self.user_id2 = user2.id
            _, self.session_token = self.session_repo.generate_session_token(self.user_id)
            for secret_id in self.secret_ids:
                self.totp_secret_repo.add(user_id=self.user_id, enc_secret="secret", uuid=secret_id)
            self.totp_secret_repo.add(user_id=self.user_id2, enc_secret="secret", uuid=self.secret_id_user2)
            db.session.commit()


        
        
    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()
    

    def test_export_vault(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            export_data = response.json()
            self.assertEqual(len(export_data.split(',')), 2)
            vault_json_string = base64.b64decode(export_data.split(',')[0]).decode("utf-8")
            signature = export_data.split(',')[1]
            self.assertTrue(API_signature().verify_rsa_signature(signature, export_data.split(',')[0]))
            vault = json.loads(vault_json_string)
            self.assertTrue(vault["version"])
            if vault["version"] == 1:
                self.assertIsNotNone(vault["date"])
                self.assertIsNotNone(vault["secrets"])
                for secret in vault["secrets"]:
                    self.assertIn(secret['uuid'], self.secret_ids)
                self.assertIsNotNone(vault["derived_key_salt"])
                self.assertIsNotNone(vault["zke_key_enc"])
                self.assertIsNotNone(vault["secrets_sha256sum"])
            else :
                raise Exception("Unknown vault version")

    def test_export_vault_no_secrets(self):    
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            self.totp_secret_repo.delete_all(self.user_id)
            db.session.commit()
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            export_data = response.json()
            self.assertEqual(len(export_data.split(',')), 2)
            vault_json_string = base64.b64decode(export_data.split(',')[0]).decode("utf-8")
            signature = export_data.split(',')[1]
            self.assertTrue(API_signature().verify_rsa_signature(signature, export_data.split(',')[0]))
            vault = json.loads(vault_json_string)
            self.assertTrue(vault["version"])
            if vault["version"] == 1:
                self.assertIsNotNone(vault["date"])
                self.assertIsNotNone(vault["secrets"])
                self.assertEqual(vault["secrets"], [])
                self.assertIsNotNone(vault["derived_key_salt"])
                self.assertIsNotNone(vault["zke_key_enc"])
                self.assertIsNotNone(vault["secrets_sha256sum"])
            else :
                raise Exception("Unknown vault version")

    def test_export_vault_user_blocked(self):
       with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            self.user_repo.update_block_status(self.user_id, True)
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "User is blocked")
    
    def test_export_vault_user_not_verified(self):
         with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            self.user_repo.update_email_verification(self.user_id, False)
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], "Not verified")



