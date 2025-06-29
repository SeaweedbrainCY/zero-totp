import unittest
from app import app
import controllers
from unittest.mock import patch
from zero_totp_db_model.model import User, ZKE_encryption_key
from database.user_repo import User as UserRepo
from environment import conf
from database.db import db 
from datetime import datetime

class TestSignupController(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.client = self.application.test_client()
        self.endpoint = "/api/v1/signup"

        with self.application.app.app_context():
            db.create_all()
            db.session.commit()
        
        self.send_verification_email = patch("controllers.send_verification_email").start()
        self.send_verification_email.return_value = True


        self.json_payload = {"username" : "username", "password": "Abcdefghij1#", "email": "test@test.py", "derivedKeySalt": "randomSalt", "ZKE_key": "encrypted_key", "passphraseSalt" :"randomSalt"}

    def tearDown(self):
         with self.application.app.app_context():
            db.session.remove()
            db.drop_all()
            patch.stopall()
        
    

    def test_signup(self):
        with self.application.app.app_context():
            response = self.client.post(self.endpoint, json=self.json_payload)
            self.assertEqual(response.status_code, 201)
            self.assertIn("Set-Cookie", response.headers)
            self.assertIn("session-token", response.headers["Set-Cookie"])
            self.assertIn("HttpOnly", response.headers["Set-Cookie"])
            self.assertIn("Secure", response.headers["Set-Cookie"])
            self.assertIn("SameSite=Lax", response.headers["Set-Cookie"])
            self.assertIn("Expires", response.headers["Set-Cookie"])
            self.send_verification_email.assert_called_once()
            user = db.session.query(User).filter(User.mail == self.json_payload["email"]).first()
            self.assertIsNotNone(user)
            self.assertIsNotNone(db.session.query(ZKE_encryption_key).filter(ZKE_encryption_key.user_id == user.id).first())
    
    def test_signup_error_while_sending_verification_email(self):
        self.send_verification_email.side_effect = Exception("error")
        response = self.client.post(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 201)
    

    def test_signup_missing_parrameters(self):
        with self.application.app.app_context():
            for key in self.json_payload.keys():
                json_payload = self.json_payload.copy()
                del json_payload[key]
                response = self.client.post(self.endpoint, json=json_payload)
                self.assertEqual(response.status_code, 400)
                self.assertIsNone(db.session.query(User).filter(User.mail == self.json_payload["email"]).first())

            for key in self.json_payload.keys():
                json_payload = self.json_payload.copy()
                json_payload[key]=""
                response = self.client.post(self.endpoint, json=json_payload)
                self.assertEqual(response.status_code, 400)
                self.assertIsNone(db.session.query(User).filter(User.mail == self.json_payload["email"]).first())
    
    def test_signup_forbidden_email(self):
        invalid_emails = [
            "plainaddress",                  # Pas de domaine
            "@nousername.com",               # Pas de nom d'utilisateur
            "user@.nodomain",                # Pas de nom de domaine
            "user@domain..com",              # Double point dans le domaine
            "user@domain,com",               # Virgule au lieu d'un point
            "user@domain com",               # Espace dans le domaine
            "userdomain.com",                # Manque le @
            "user@-domain.com",              # Domaine commençant par un tiret
            "user@domain.com.",              # Point final après le domaine
            "user@domain..com",              # Domaine avec double point
            "user@.domain.com",              # Domaine commençant par un point
            "user@.com",                     # Pas de nom de domaine
            ".user@domain.com",              # Nom d'utilisateur commençant par un point
            "user.@domain.com",              # Nom d'utilisateur se terminant par un point
            "user..name@domain.com",         # Double point dans le nom d'utilisateur
            "user@domain@domain.com",        # Deux @
            "user@domain/com",               # Slash au lieu de point
            "user@domain#com",               # Symbole non autorisé
        ]

        with self.application.app.app_context():
            for email in invalid_emails:
                self.json_payload["email"] = email
                response = self.client.post(self.endpoint, json=self.json_payload)
                self.assertEqual(response.status_code, 401, f"Email : {email}")
                self.assertIsNone(db.session.query(User).filter(User.mail == self.json_payload["email"]).first(), f"Email : {email}")
    
    
    def test_signup_user_already_exists(self):
        with self.application.app.app_context():
            UserRepo().create(username="username2", email=self.json_payload["email"], password="password", randomSalt="salt", passphraseSalt="salt", today=datetime.now())
            response = self.client.post(self.endpoint, json=self.json_payload)
            self.assertEqual(response.status_code, 409)
    
    def test_signup_password_too_long(self):
        self.json_payload["password"] = "a"*322
        response = self.client.post(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 400)


    def test_signup_user_already_exists(self):
        with self.application.app.app_context():
            UserRepo().create(username=self.json_payload["username"], email="username2@mail.com", password="password", randomSalt="salt", passphraseSalt="salt", today=datetime.now())
            response = self.client.post(self.endpoint, json=self.json_payload)
            self.assertEqual(response.status_code, 409)
    
    def test_signup_username_too_long(self):
        self.json_payload["username"] = "a"*322
        response = self.client.post(self.endpoint, json=self.json_payload)
        self.assertEqual(response.status_code, 400)


    def test_signup_when_signup_disabled(self):
        with patch.object(conf.features, 'signup_enabled', False):
            with self.application.app.app_context():
                response = self.client.post(self.endpoint, json=self.json_payload)
                self.assertEqual(response.status_code, 403)
                self.assertEqual(response.json["code"], "signup_disabled")
                self.assertIsNone(db.session.query(User).filter(User.mail == self.json_payload["email"]).first())

    

   
    
    


    
    
