import unittest
from app import app
from database.db import db 
import controllers
from unittest.mock import patch
from database.user_repo import User as UserRepo
from database.totp_secret_repo import TOTP_secret as TOTPRepo
from database.session_token_repo import SessionTokenRepo
from zero_totp_db_model.model  import TOTP_secret 
from environment import conf
import datetime
from uuid import uuid4

class TestEncryptedSecretController(unittest.TestCase):
    USER_NOT_VERIFIED_ERROR_MESSAGE = "Not verified"
    USER_BLOCKED_ERROR_MESSAGE = "User is blocked"

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/api/v1/encrypted_secret"
        self.secret_ids = [str(uuid4()) for _ in range(3)]
        self.secret_id_user2 = str(uuid4())
        
        self.user_repo = UserRepo()
        self.totp_secret_repo = TOTPRepo()
        self.session_repo = SessionTokenRepo()

        with self.flask_application.app.app_context():
            db.create_all()
            user = self.user_repo.create(username='user1', email='user1@test.com', password='test', randomSalt='salt', passphraseSalt='salt', today=datetime.datetime.now(), isVerified=True)
            self.user_id = user.id
            user2 = self.user_repo.create(username='user2', email='user2@test.com', password='test', randomSalt='salt', passphraseSalt='salt', today=datetime.datetime.now(), isVerified=True)
            self.user_id2 = user2.id
            _, self.session_token = self.session_repo.generate_session_token(self.user_id)
            for secret_id in self.secret_ids:
                self.totp_secret_repo.add(user_id=self.user_id, enc_secret="secret", uuid=secret_id)
            self.totp_secret_repo.add(user_id=self.user_id2, enc_secret="secret", uuid=self.secret_id_user2)
            db.session.commit()




        self.json_payload = {"enc_secret": str(uuid4())}


    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()

    
    
######
## GET
######


    def test_get_encrypted_secret(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            for secret_id in self.secret_ids:
                response = self.client.get(f"{self.endpoint}/{secret_id}")
                self.assertEqual(response.status_code, 200, f"Failed to get secret with id {secret_id}. Was expecting status code 200, got {response.status_code}. Response: {response.json()}")
                self.assertIn("enc_secret", response.json())
    

    
    def test_get_encrypted_secret_no_secret(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            db.session.query(TOTP_secret).delete()
            response = self.client.get(f"{self.endpoint}/{str(uuid4())}")
            self.assertEqual(response.status_code, 403)
    

    def test_get_encrypted_secret_of_another_user(self):
         with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.get(f"{self.endpoint}/{self.secret_id_user2}")
            self.assertEqual(response.status_code, 403)

    def test_get_encrypted_secret_user_blocked(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            self.user_repo.update_block_status(self.user_id, True)
            response = self.client.get(f"{self.endpoint}/{str(uuid4())}")
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], self.USER_BLOCKED_ERROR_MESSAGE)
    
    def test_get_encrypted_secret_user_unverified(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            self.user_repo.update_email_verification(self.user_id, False)
            response = self.client.get(f"{self.endpoint}/{str(uuid4())}")
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], self.USER_NOT_VERIFIED_ERROR_MESSAGE)


########
### POST
########

    def test_post_encrypted_secret(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.post(self.endpoint, json=self.json_payload)
            self.assertEqual(response.status_code, 201)
            self.assertIsNotNone(response.json()["uuid"])
            self.assertEqual(self.totp_secret_repo.get_enc_secret_by_uuid(response.json()["uuid"]).secret_enc, self.json_payload["enc_secret"])
            self.assertEqual(self.totp_secret_repo.get_enc_secret_by_uuid(response.json()["uuid"]).user_id, self.user_id)
            
   
    def test_post_encrypted_secret_user_blocked(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            self.user_repo.update_block_status(self.user_id, True)
            response = self.client.post(self.endpoint, json=self.json_payload)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], self.USER_BLOCKED_ERROR_MESSAGE)
    
    def test_post_encrypted_secret_user_unverified(self):
       with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            self.user_repo.update_email_verification(self.user_id, False)
            response = self.client.post(self.endpoint, json=self.json_payload)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], self.USER_NOT_VERIFIED_ERROR_MESSAGE)

#######
### PUT
#######


    def test_update_encrypted_secret(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.put(f"{self.endpoint}/{self.secret_ids[0]}", json=self.json_payload)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(self.totp_secret_repo.get_enc_secret_by_uuid(self.secret_ids[0]).secret_enc, self.json_payload["enc_secret"])
    
    
    def test_update_encrypted_secret_no_exists(self):
         with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.put(f"{self.endpoint}/{str(uuid4())}", json=self.json_payload)
            self.assertEqual(response.status_code, 403)
    
    def test_update_encrypted_secret_wrong_user(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.put(f"{self.endpoint}/{self.secret_id_user2}", json=self.json_payload)
            self.assertEqual(response.status_code, 403)
    

#
    def test_update_encrypted_secret_user_blocked(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            self.user_repo.update_block_status(self.user_id, True)
            response = self.client.put(f"{self.endpoint}/{self.secret_ids[0]}", json=self.json_payload)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], self.USER_BLOCKED_ERROR_MESSAGE)
    
    def test_update_encrypted_secret_user_unverified(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            self.user_repo.update_email_verification(self.user_id, False)
            response = self.client.put(f"{self.endpoint}/{self.secret_ids[0]}", json=self.json_payload)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], self.USER_NOT_VERIFIED_ERROR_MESSAGE)


##########
### DELETE
##########



    def test_delete_encrypted_secret(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.delete(f"{self.endpoint}/{self.secret_ids[0]}")
            self.assertEqual(response.status_code, 201)
            self.assertIsNone(self.totp_secret_repo.get_enc_secret_by_uuid(self.secret_ids[0]))
    

    def test_delete_encrypted_secret_no_exists(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.delete(f"{self.endpoint}/{str(uuid4())}")
            self.assertEqual(response.status_code, 403)
    

    def test_delete_encrypted_secret_wrong_user(self):
         with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            response = self.client.delete(f"{self.endpoint}/{self.secret_id_user2}")
            self.assertEqual(response.status_code, 403)
    

    
    def test_delete_encrypted_secret_user_blocked(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            self.user_repo.update_block_status(self.user_id, True)
            response = self.client.delete(f"{self.endpoint}/{self.secret_ids[0]}")
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], self.USER_BLOCKED_ERROR_MESSAGE)
    
    def test_delete_encrypted_secret_user_unverified(self):
         with self.flask_application.app.app_context():
            self.client.cookies = {"session-token": self.session_token}
            self.user_repo.update_email_verification(self.user_id, False)
            response = self.client.delete(f"{self.endpoint}/{self.secret_ids[0]}")
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["error"], self.USER_NOT_VERIFIED_ERROR_MESSAGE)
