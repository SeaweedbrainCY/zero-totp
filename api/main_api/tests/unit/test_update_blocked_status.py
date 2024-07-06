import unittest
from main_api.app import app
from db_models.db import db 
from main_api.environment import conf
from db_models.model import User as UserModel, Admin as AdminModel
from main_api.db_repo.user_repo import User as UserDB
from unittest.mock import patch
from main_api.CryptoClasses.jwt_func import generate_jwt, verify_jwt, ISSUER as jwt_ISSUER, ALG as jwt_ALG
import datetime

class TestUpdateBlockedStatus(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.application = app
        self.client = self.application.test_client()
        self.getUpdateEndpoint = "/admin/account/"
        self.admin_user_id = 1
        self.normal_user_id = 2

        admin_user = UserModel(id=self.admin_user_id,username="admin", mail="admin@admin.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role="admin")
        normal_user = UserModel(id=self.normal_user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", role=None)
        admin_user_token = AdminModel(user_id=self.admin_user_id, token_hashed="token", token_expiration=(datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).timestamp())
        with self.application.app.app_context():
            db.create_all()
            db.session.add(admin_user)
            db.session.add(admin_user_token)
            db.session.add(normal_user)
            db.session.commit()
           
    def tearDown(self):
        with self.application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()
    

    def test_block_user(self):
        with self.application.app.app_context():
           self.client.cookies = {"api-key":generate_jwt(self.admin_user_id),"admin-api-key":generate_jwt(self.admin_user_id, admin=True)}
           response = self.client.put(self.getUpdateEndpoint + f"{self.normal_user_id}/block")
           self.assertEqual(response.status_code, 201)
           user_obj = UserDB().getById(self.normal_user_id)
           self.assertTrue(user_obj.isBlocked)
    
    def test_unblock_user(self):
        with self.application.app.app_context():
           self.client.cookies = {"api-key":generate_jwt(self.admin_user_id),"admin-api-key":generate_jwt(self.admin_user_id, admin=True)}
           response = self.client.put(self.getUpdateEndpoint  + f"{self.normal_user_id}/unblock")
           self.assertEqual(response.status_code, 201)
           user_obj = UserDB().getById(self.normal_user_id)
           self.assertFalse(user_obj.isBlocked)
    
    def test_update_user_unknown_action(self):
        with self.application.app.app_context():
           self.client.cookies = {"api-key":generate_jwt(self.admin_user_id),"admin-api-key":generate_jwt(self.admin_user_id, admin=True)}
           response = self.client.put(self.getUpdateEndpoint  + f"{self.normal_user_id}/random")
           self.assertEqual(response.status_code, 400)
    
    def test_update_user_not_found(self):
        with self.application.app.app_context():
           self.client.cookies = {"api-key":generate_jwt(self.admin_user_id),"admin-api-key":generate_jwt(self.admin_user_id, admin=True)}
           response = self.client.put(self.getUpdateEndpoint  + f"{self.normal_user_id+1}/block")
           self.assertEqual(response.status_code, 404)
    
    def test_block_admin(self):
        with self.application.app.app_context():
           self.client.cookies = {"api-key":generate_jwt(self.admin_user_id),"admin-api-key":generate_jwt(self.admin_user_id, admin=True)}
           response = self.client.put(self.getUpdateEndpoint  + f"{self.admin_user_id}/block")
           self.assertEqual(response.status_code, 403)
    
    def test_block_user_not_admin(self):
        with self.application.app.app_context():
           self.client.cookies = {"api-key":generate_jwt(self.normal_user_id),"admin-api-key":generate_jwt(self.normal_user_id, admin=False)}
           response = self.client.put(self.getUpdateEndpoint  + f"{self.normal_user_id}/block")
           self.assertEqual(response.status_code, 403)
    
    def test_unblock_user_no_admin_cookie(self):
        with self.application.app.app_context():
           self.client.cookies = {"api-key":generate_jwt(self.normal_user_id),"admin-api-key":generate_jwt(self.normal_user_id, admin=False)}
           response = self.client.put(self.getUpdateEndpoint  + f"{self.normal_user_id}/unblock")
           self.assertEqual(response.status_code, 403)
    
    