from Utils import security_wrapper
import unittest
from unittest.mock import patch
from database.model import User as UserModel, Admin as AdminModel
from database.db import db
from app import app


class TestSecurityWrapper(unittest.TestCase):
    
        def setUp(self):
            self.not_verified_user_id = 1
            self.verified_user_id = 2
            self.flask_application = app
    
            not_verified_user = UserModel(id=self.not_verified_user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = False, passphraseSalt = "AAAA", createdAt="01/01/2001")
            verified_user_id = UserModel(id=self.verified_user_id,username="user", mail="user@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001")
            with self.flask_application.app.app_context():
                db.create_all()
                db.session.add(not_verified_user)
                db.session.add(verified_user_id)
                db.session.commit()
        
        def tearDown(self):
            with self.flask_application.app.app_context():
                db.session.remove()
                db.drop_all()
                patch.stopall()
        
        
        
        def test_valid_user_not_verified_and_require(self):
            security_wrapper.require_email_validation = True
            @security_wrapper.require_valid_user
            def wrapped_function(user_id):
                return True, 200
            with self.flask_application.app.app_context():
                _, status = wrapped_function({"user": self.not_verified_user_id},self.not_verified_user_id, {"user": self.not_verified_user_id})
                self.assertEqual(status, 403)
        
        def test_valid_user_verified_and_require(self):
            security_wrapper.require_email_validation = True
            @security_wrapper.require_valid_user
            def wrapped_function(user_id):
                return True, 200
            with self.flask_application.app.app_context():
                _, status = wrapped_function({"user": self.verified_user_id},self.verified_user_id, {"user": self.verified_user_id})
                self.assertEqual(status, 200)
        
        def test_valid_user_not_verified_and_not_require(self):
            security_wrapper.require_email_validation = False
            @security_wrapper.require_valid_user
            def wrapped_function(user_id):
                return True, 200
            with self.flask_application.app.app_context():
                _, status = wrapped_function({"user": self.not_verified_user_id},self.not_verified_user_id, {"user": self.not_verified_user_id})
                self.assertEqual(status, 200)
        
        def test_valid_user_verified_and_not_require(self):
            security_wrapper.require_email_validation = False
            @security_wrapper.require_valid_user
            def wrapped_function(user_id):
                return True, 200
            with self.flask_application.app.app_context():
                _, status = wrapped_function({"user": self.verified_user_id},self.verified_user_id, {"user": self.verified_user_id})
                self.assertEqual(status, 200)

             
