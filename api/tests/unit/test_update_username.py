import unittest
from app import app
from database.db import db 
import environment as env
from unittest.mock import patch
from CryptoClasses.jwt_func import generate_jwt, ISSUER as jwt_ISSUER, ALG as jwt_ALG
import datetime
from database.model import User as UserModel


class TestUpdateUsername(unittest.TestCase):

    def setUp(self) -> None:
        if env.db_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        self.client = self.flask_application.test_client()
        self.endpoint = "/update/username"
        self.user1_id = 1
        self.user2_id = 2

        
        user1 = UserModel(id=self.user1_id,username='user1', mail="user1@test.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001")
        user2 = UserModel(id=self.user2_id,username='user2', mail="user2@test.com",password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001")
        with self.flask_application.app.app_context():
            db.create_all()
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
    
    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()

    
    def test_update_username(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key": generate_jwt(self.user1_id)}
            response = self.client.put(self.endpoint, json={"username": "new_username"})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(db.session.query(UserModel).filter_by(id=self.user1_id).first().username, "new_username")
    
    def test_update_username_already_taken(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key": generate_jwt(self.user1_id)}
            response = self.client.put(self.endpoint, json={"username": "user2"})
            self.assertEqual(response.status_code, 409)
    
    def test_update_username_cookie(self):
        with self.flask_application.app.app_context():
            response = self.client.put(self.endpoint, json={"username": "new_username"})
            self.assertEqual(response.status_code, 401)
    
    def test_update_username_bad_cookie(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key": "bad"}
            response = self.client.put(self.endpoint, json={"username": "new_username"})
            self.assertEqual(response.status_code, 403)
    
    def test_update_username_disabled_user(self):
        with self.flask_application.app.app_context():
            user = db.session.query(UserModel).filter_by(id=self.user1_id).first()
            user.isVerified = False
            db.session.commit()
            self.client.cookies = {"api-key": generate_jwt(self.user1_id)}
            response = self.client.put(self.endpoint, json={"username": "new_username"})
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json(), {"error": "Not verified"})
     
     def test_update_username_too_long(self):
        with self.flask_application.app.app_context():
            self.client.cookies = {"api-key": generate_jwt(self.user1_id)}
            response = self.client.put(self.endpoint, json={"username": "a"*321})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {"error": "Username too long"})
