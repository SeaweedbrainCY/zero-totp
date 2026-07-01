
from app import app
from Utils import security_wrapper
import unittest
from unittest.mock import patch
from zero_totp_db_model.model import User as UserModel
from database.db import db
from connexion.testing import TestContext



class TestSecurityWrapper(unittest.TestCase):
    
        def setUp(self):
            self.not_verified_user_id = 1
            self.verified_user_id = 2
            self.blocked_user_id = 3
            self.flask_application = app
    
            not_verified_user = UserModel(id=self.not_verified_user_id,username="user1", mail="user1@user.com", password="pass", derivedKeySalt="AAA", isVerified = False, passphraseSalt = "AAAA", createdAt="01/01/2001")
            verified_user_id = UserModel(id=self.verified_user_id,username="user2", mail="user2@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001")
            blocked_user_id = UserModel(id=self.blocked_user_id,username="user3", mail="user3@user.com", password="pass", derivedKeySalt="AAA", isVerified = True, passphraseSalt = "AAAA", createdAt="01/01/2001", isBlocked = True)
            with self.flask_application.app.app_context():
                db.create_all()
                db.session.add(not_verified_user)
                db.session.add(verified_user_id)
                db.session.add(blocked_user_id)
                db.session.commit()

        
        def tearDown(self):
            with self.flask_application.app.app_context():
                db.session.remove()
                db.drop_all()
                patch.stopall()
        
        @security_wrapper.require_active_user
        def wrapped_function(self,src_ip, user_obj):
            return {"user_id" : user_obj.id}, 200
        
        
        
        def test_valid_user_not_verified_and_require(self):
            security_wrapper.conf.features.emails.require_email_validation = True
            with TestContext(context={"token_info": {"uid": self.not_verified_user_id}}):
                    with self.flask_application.app.app_context():
                        response, status = self.wrapped_function()
                        self.assertEqual(status, 403)
                        self.assertEqual(response, {'error': 'Not verified'})

        
        def test_valid_user_verified_and_require(self):
            security_wrapper.conf.features.emails.require_email_validation = True
            with TestContext(context={"token_info": {"uid": self.verified_user_id}}):
                with self.flask_application.app.app_context():
                    response, status = self.wrapped_function()
                    self.assertEqual(status, 200)
                    self.assertEqual(response, {"user_id":self.verified_user_id})
        
        def test_valid_user_not_verified_and_not_require(self):
            security_wrapper.conf.features.emails.require_email_validation = False
            with TestContext(context={"token_info": {"uid": self.not_verified_user_id}}):
                 with self.flask_application.app.app_context():
                    response, status = self.wrapped_function()
                    self.assertEqual(status, 200)
                    self.assertEqual(response, {"user_id":self.not_verified_user_id})
                    
        
        def test_valid_user_verified_and_not_require(self):
            security_wrapper.conf.features.emails.require_email_validation = False
            with TestContext(context={"token_info": {"uid": self.verified_user_id}}):
                with self.flask_application.app.app_context():
                    response, status = self.wrapped_function()
                    self.assertEqual(status, 200)
                    self.assertEqual(response, {"user_id":self.verified_user_id})

        
        def test_valid_user_blocked(self):
            with TestContext(context={"token_info": {"uid": self.blocked_user_id}}):
                with self.flask_application.app.app_context():
                    response, status = self.wrapped_function()
                    self.assertEqual(status, 403)
                    self.assertEqual(response, {'error': 'User is blocked'})

        def test_require_userid_blocked(self):
            security_wrapper.conf.features.emails.require_email_validation = True
            @security_wrapper.require_userid
            def wrapped_function(src_ip, user_id):
                return True, 200
            with TestContext(context={"token_info": {"uid": self.blocked_user_id}}):
                with self.flask_application.app.app_context():
                    response, status = wrapped_function({"user": self.blocked_user_id},self.blocked_user_id, {"user": self.blocked_user_id})
                    self.assertEqual(status, 403)
                    self.assertEqual(response, {'error': 'User is blocked'})
