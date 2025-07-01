import unittest
from app import app
from database.db import db 
import datetime
from uuid import uuid4
from environment import conf
from database.session_token_repo import SessionTokenRepo
from database.user_repo import User as UserRepo
from zero_totp_db_model.model import SessionToken



class TestEndpointProtection(unittest.TestCase):

    get_endpoint_requiring_session = ["/api/v1/role", "/api/v1/zke_encrypted_key", f"/api/v1/encrypted_secret/{str(uuid4())}", "/api/v1/all_secrets", "/api/v1/vault/export", "api/v1/preferences", "/api/v1/whoami", "/api/v1/google-drive/oauth/authorization-flow", "/api/v1/google-drive/oauth/callback", "/api/v1/google-drive/option", "/api/v1/google-drive/last-backup/verify", "/api/v1/notification/internal", "/api/v1/email/send_verification", "/api/v1/backup/configuration", "/api/v1/backup/configuration?dv=true", "/api/v1/user/derived-key-salt", "/api/v1/backup/server/options"]

    post_endpoint_requiring_session = [f"/api/v1/encrypted_secret"]

    put_endpoint_requiring_session = [f"/api/v1/encrypted_secret/{str(uuid4())}", "/api/v1/update/email", "/api/v1/update/username", "/api/v1/update/vault", "/api/v1/preferences", "/api/v1/email/verify", "/api/v1/google-drive/backup", "/api/v1/backup/configuration/max_age_in_days", "/api/v1/backup/configuration/backup_minimum_count"]

    delete_endpoint_requiring_session = [f"/api/v1/encrypted_secret/{str(uuid4())}", "/api/v1/account", "/api/v1/google-drive/option",  "/api/v1/google-drive/backup" ]

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.user_id = 1 
        with self.flask_application.app.app_context():
            db.create_all()
            user = UserRepo().create(username='username', email='username@test.com', password='test', randomSalt='salt', passphraseSalt='salt', today=datetime.datetime.now(), isVerified=True)
            self.user_id = user.id
            self.session_id, self.session_token = SessionTokenRepo().generate_session_token(self.user_id)
            db.session.commit()
    
    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
    
#######
## GET
#######

    def test_endpoint_session_with_valid_user_GET_no_cookie(self):
         for get_endpoint in self.get_endpoint_requiring_session:
            with self.flask_application.app.app_context():
                response = self.client.get(get_endpoint)
                self.assertEqual(response.status_code, 401, f"GET {get_endpoint} should return 401. Got {response.status_code}. Response: {response.json()}")
                self.assertEqual(response.json()['detail'], 'No authorization token provided', f"GET {get_endpoint} got {response.json()}")
    
    def test_endpoint_session_with_valid_user_GET_unknown_session(self):
         for get_endpoint in self.get_endpoint_requiring_session:
            with self.flask_application.app.app_context():
                self.client.cookies = {'session-token': str(uuid4())}
                response = self.client.get(get_endpoint)
                self.assertEqual(response.status_code, 403, f"GET {get_endpoint} should return 403. Got {response.status_code}")
                self.assertEqual(response.json()['detail'], 'Invalid session token', f"GET {get_endpoint} got {response.json()}")
    
    def test_endpoint_session_with_valid_user_GET_revoked_session(self):
            with self.flask_application.app.app_context():
                 SessionTokenRepo().revoke(self.session_id)
            for get_endpoint in self.get_endpoint_requiring_session:
                with self.flask_application.app.app_context():
                    self.client.cookies = {'session-token': self.session_token}
                    response = self.client.get(get_endpoint)
                    self.assertEqual(response.status_code, 403, f"GET {get_endpoint} should return 403. Got {response.status_code}")
                    self.assertEqual(response.json()['detail'], 'Invalid session token', f"GET {get_endpoint} got {response.json()}")
    
    def test_endpoint_session_with_valid_user_GET_expired_session(self):
            with self.flask_application.app.app_context():
                db.session.query(SessionToken).filter(SessionToken.id == self.session_id).update({"expiration": (datetime.datetime.now() - datetime.timedelta(days=1)).timestamp()})
                db.session.commit()
            for get_endpoint in self.get_endpoint_requiring_session:
                with self.flask_application.app.app_context():
                    self.client.cookies = {'session-token': self.session_token}
                    response = self.client.get(get_endpoint)
                    self.assertEqual(response.status_code, 403, f"GET {get_endpoint} should return 403. Got {response.status_code}")
                    self.assertEqual(response.json()['detail'], 'API key expired', f"GET {get_endpoint} got {response.json()}")
    
    
########
## POST
########

    def test_endpoint_session_with_valid_user_POST_no_cookie(self):
         for post_endpoint in self.post_endpoint_requiring_session:
            with self.flask_application.app.app_context():
                response = self.client.post(post_endpoint)
                self.assertEqual(response.status_code, 401, f"POST {post_endpoint} should return 401. Got {response.status_code}. Response: {response.json()}")
                self.assertEqual(response.json()['detail'], 'No authorization token provided', f"POST {post_endpoint} got {response.json()}")
    
    def test_endpoint_session_with_valid_user_POST_unknown_session(self):
         for post_endpoint in self.post_endpoint_requiring_session:
            with self.flask_application.app.app_context():
                self.client.cookies = {'session-token': str(uuid4())}
                response = self.client.post(post_endpoint)
                self.assertEqual(response.status_code, 403, f"POST {post_endpoint} should return 403. Got {response.status_code}")
                self.assertEqual(response.json()['detail'], 'Invalid session token', f"POST {post_endpoint} got {response.json()}")
    
    def test_endpoint_session_with_valid_user_POST_revoked_session(self):
            with self.flask_application.app.app_context():
                 SessionTokenRepo().revoke(self.session_id)
            for post_endpoint in self.post_endpoint_requiring_session:
                with self.flask_application.app.app_context():
                    self.client.cookies = {'session-token': self.session_token}
                    response = self.client.post(post_endpoint)
                    self.assertEqual(response.status_code, 403, f"POST {post_endpoint} should return 403. Got {response.status_code}")
                    self.assertEqual(response.json()['detail'], 'Invalid session token', f"POST {post_endpoint} got {response.json()}")
    
    def test_endpoint_session_with_valid_user_POST_expired_session(self):
            with self.flask_application.app.app_context():
                db.session.query(SessionToken).filter(SessionToken.id == self.session_id).update({"expiration": (datetime.datetime.now() - datetime.timedelta(days=1)).timestamp()})
                db.session.commit()
            for post_endpoint in self.post_endpoint_requiring_session:
                with self.flask_application.app.app_context():
                    self.client.cookies = {'session-token': self.session_token}
                    response = self.client.post(post_endpoint)
                    self.assertEqual(response.status_code, 403, f"POST {post_endpoint} should return 403. Got {response.status_code}")
                    self.assertEqual(response.json()['detail'], 'API key expired', f"POST {post_endpoint} got {response.json()}")                    

########
## PUT
########

    def test_endpoint_session_with_valid_user_PUT_no_cookie(self):
         for put_endpoint in self.put_endpoint_requiring_session:
            with self.flask_application.app.app_context():
                response = self.client.put(put_endpoint)
                self.assertEqual(response.status_code, 401, f"PUT {put_endpoint} should return 401. Got {response.status_code}. Response: {response.json()}")
                self.assertEqual(response.json()['detail'], 'No authorization token provided', f"PUT {put_endpoint} got {response.json()}")
    
    def test_endpoint_session_with_valid_user_PUT_unknown_session(self):
         for put_endpoint in self.put_endpoint_requiring_session:
            with self.flask_application.app.app_context():
                self.client.cookies = {'session-token': str(uuid4())}
                response = self.client.put(put_endpoint)
                self.assertEqual(response.status_code, 403, f"PUT {put_endpoint} should return 403. Got {response.status_code}")
                self.assertEqual(response.json()['detail'], 'Invalid session token', f"PUT {put_endpoint} got {response.json()}")
    
    def test_endpoint_session_with_valid_user_PUT_revoked_session(self):
            with self.flask_application.app.app_context():
                 SessionTokenRepo().revoke(self.session_id)
            for put_endpoint in self.put_endpoint_requiring_session:
                with self.flask_application.app.app_context():
                    self.client.cookies = {'session-token': self.session_token}
                    response = self.client.put(put_endpoint)
                    self.assertEqual(response.status_code, 403, f"PUT {put_endpoint} should return 403. Got {response.status_code}")
                    self.assertEqual(response.json()['detail'], 'Invalid session token', f"PUT {put_endpoint} got {response.json()}")
    
    def test_endpoint_session_with_valid_user_PUT_expired_session(self):
            with self.flask_application.app.app_context():
                db.session.query(SessionToken).filter(SessionToken.id == self.session_id).update({"expiration": (datetime.datetime.now() - datetime.timedelta(days=1)).timestamp()})
                db.session.commit()
            for put_endpoint in self.put_endpoint_requiring_session:
                with self.flask_application.app.app_context():
                    self.client.cookies = {'session-token': self.session_token}
                    response = self.client.put(put_endpoint)
                    self.assertEqual(response.status_code, 403, f"PUT {put_endpoint} should return 403. Got {response.status_code}")
                    self.assertEqual(response.json()['detail'], 'API key expired', f"PUT {put_endpoint} got {response.json()}")


#########
## DELETE
#########

    def test_endpoint_session_with_valid_user_DELETE_no_cookie(self):
         for delete_endpoint in self.delete_endpoint_requiring_session:
            with self.flask_application.app.app_context():
                response = self.client.delete(delete_endpoint)
                self.assertEqual(response.status_code, 401, f"DELETE {delete_endpoint} should return 401. Got {response.status_code}. Response: {response.json()}")
                self.assertEqual(response.json()['detail'], 'No authorization token provided', f"DELETE {delete_endpoint} got {response.json()}")
    
    def test_endpoint_session_with_valid_user_DELETE_unknown_session(self):
         for delete_endpoint in self.delete_endpoint_requiring_session:
            with self.flask_application.app.app_context():
                self.client.cookies = {'session-token': str(uuid4())}
                response = self.client.delete(delete_endpoint)
                self.assertEqual(response.status_code, 403, f"DELETE {delete_endpoint} should return 403. Got {response.status_code}")
                self.assertEqual(response.json()['detail'], 'Invalid session token', f"DELETE {delete_endpoint} got {response.json()}")
    
    def test_endpoint_session_with_valid_user_DELETE_revoked_session(self):
            with self.flask_application.app.app_context():
                 SessionTokenRepo().revoke(self.session_id)
            for delete_endpoint in self.delete_endpoint_requiring_session:
                with self.flask_application.app.app_context():
                    self.client.cookies = {'session-token': self.session_token}
                    response = self.client.delete(delete_endpoint)
                    self.assertEqual(response.status_code, 403, f"DELETE {delete_endpoint} should return 403. Got {response.status_code}")
                    self.assertEqual(response.json()['detail'], 'Invalid session token', f"DELETE {delete_endpoint} got {response.json()}")
    
    def test_endpoint_session_with_valid_user_DELETE_expired_session(self):
            with self.flask_application.app.app_context():
                db.session.query(SessionToken).filter(SessionToken.id == self.session_id).update({"expiration": (datetime.datetime.now() - datetime.timedelta(days=1)).timestamp()})
                db.session.commit()
            for delete_endpoint in self.delete_endpoint_requiring_session:
                with self.flask_application.app.app_context():
                    self.client.cookies = {'session-token': self.session_token}
                    response = self.client.delete(delete_endpoint)
                    self.assertEqual(response.status_code, 403, f"DELETE {delete_endpoint} should return 403. Got {response.status_code}")
                    self.assertEqual(response.json()['detail'], 'API key expired', f"DELETE {delete_endpoint} got {response.json()}")