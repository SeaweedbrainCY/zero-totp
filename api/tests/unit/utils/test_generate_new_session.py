import unittest
from app import app
from database.db import db 
from environment import conf
from database.user_repo import User as UserRepo
from Utils import utils
from zero_totp_db_model.model import User as UserModel, SessionToken as SessionTokenModel, RefreshToken as RefreshTokenModel, Session as SessionModel
import datetime as dt
from hashlib import sha256


class TestGenerateNewSession(unittest.TestCase):

    def setUp(self):
        if conf.database.database_uri != "sqlite:///:memory:":
            raise Exception("Test must be run with in memory database")
        self.flask_application = app
        user_repo = UserRepo()

        with self.flask_application.app.app_context():
            db.create_all()
            user = user_repo.create(
                username="user1", 
                email="user@zero-totp.com",
                password="password",
                randomSalt="salt",
                passphraseSalt="salt",
                isVerified=True,
                today="01/01/2001"
            )
            self.user_id = user.id

            user2 = user_repo.create(
                username="user2",
                email="user2@zero-totp.com",
                password="password2",
                randomSalt="salt",
                passphraseSalt="salt",
                isVerified=True,
                today="01/01/2001"
            )
            self.user2_id = user2.id
            db.session.commit()
            


    def tearDown(self):
        with self.flask_application.app.app_context():
            db.session.remove()
            db.drop_all()


    def test_generate_new_session_with_None_address(self):
        with self.flask_application.app.app_context():
            user = db.session.query(UserModel).filter_by(id=self.user_id).one()
            session_token, refresh_token = utils.generate_new_session(user=user,   ip_address=None)
            refresh_token_hashed = sha256(refresh_token.encode('utf-8')).hexdigest()


            self.assertIsInstance(session_token, str)
            self.assertIsInstance(refresh_token, str)

        
            session_token_entry = db.session.query(SessionTokenModel).filter_by(token=session_token).one()
            refresh_token_entry = db.session.query(RefreshTokenModel).filter_by(hashed_token=refresh_token_hashed).one()
            session_entry = db.session.query(SessionModel).filter_by(id=session_token_entry.session_id).one()

            self.assertIsNotNone(session_token_entry)
            self.assertIsNotNone(refresh_token_entry)
            self.assertIsNotNone(session_entry)

            self.assertEqual(session_token_entry.user_id, user.id)
            session_token_expiration_timestamp = dt.datetime.fromtimestamp(float(session_token_entry.expiration))
            self.assertTrue((dt.datetime.now() + dt.timedelta(seconds=conf.api.session_token_validity)) - session_token_expiration_timestamp < dt.timedelta(minutes=1))
            self.assertIsNone(session_entry.revoke_timestamp)
            self.assertEqual(session_token_entry.session_id, session_entry.id)


            self.assertEqual(refresh_token_entry.user_id, user.id)
            refresh_token_expiration_timestamp = dt.datetime.fromtimestamp(float(refresh_token_entry.expiration))
            self.assertTrue((dt.datetime.now() + dt.timedelta(seconds=conf.api.refresh_token_validity)) - refresh_token_expiration_timestamp < dt.timedelta(minutes=1))
            self.assertEqual(refresh_token_entry.session_id, session_entry.id)
            self.assertEqual(refresh_token_entry.session_token_id, session_token_entry.id)
            self.assertIsNone(refresh_token_entry.revoke_timestamp)

            self.assertEqual(session_entry.user_id, user.id)
            self.assertIsNone(session_entry.ip_address)
            self.assertTrue((dt.datetime.now() -  dt.datetime.fromtimestamp(float(session_entry.created_at))) < dt.timedelta(minutes=1))
            self.assertTrue((dt.datetime.now() -  dt.datetime.fromtimestamp(float(session_entry.last_active_at))) < dt.timedelta(minutes=1))
            self.assertTrue((dt.datetime.now() + dt.timedelta(seconds=conf.api.session_validity) -  dt.datetime.fromtimestamp(float(session_entry.expiration_timestamp))) < dt.timedelta(minutes=1))


    def test_generate_new_session_with_None_address_alongside_other_sessions(self):
        with self.flask_application.app.app_context():
            user = db.session.query(UserModel).filter_by(id=self.user_id).one()
            user2 = db.session.query(UserModel).filter_by(id=self.user2_id).one()
            session_token, refresh_token = utils.generate_new_session(user=user,   ip_address=None)
            refresh_token_hashed = sha256(refresh_token.encode('utf-8')).hexdigest()

            utils.generate_new_session(user=user, ip_address=None)
            utils.generate_new_session(user=user2, ip_address=None)

            self.assertIsInstance(session_token, str)
            self.assertIsInstance(refresh_token, str)

       
            session_token_entry = db.session.query(SessionTokenModel).filter_by(token=session_token).one()
            refresh_token_entry = db.session.query(RefreshTokenModel).filter_by(hashed_token=refresh_token_hashed).one()
            session_entry = db.session.query(SessionModel).filter_by(id=session_token_entry.session_id).one()

            self.assertIsNotNone(session_token_entry)
            self.assertIsNotNone(refresh_token_entry)
            self.assertIsNotNone(session_entry)

            self.assertEqual(session_token_entry.user_id, user.id)
            session_token_expiration_timestamp = dt.datetime.fromtimestamp(float(session_token_entry.expiration))
            self.assertTrue((dt.datetime.now() + dt.timedelta(seconds=conf.api.session_token_validity)) - session_token_expiration_timestamp < dt.timedelta(minutes=1))
            self.assertIsNone(session_entry.revoke_timestamp)
            self.assertEqual(session_token_entry.session_id, session_entry.id)


            self.assertEqual(refresh_token_entry.user_id, user.id)
            refresh_token_expiration_timestamp = dt.datetime.fromtimestamp(float(refresh_token_entry.expiration))
            self.assertTrue((dt.datetime.now() + dt.timedelta(seconds=conf.api.refresh_token_validity)) - refresh_token_expiration_timestamp < dt.timedelta(minutes=1))
            self.assertEqual(refresh_token_entry.session_id, session_entry.id)
            self.assertEqual(refresh_token_entry.session_token_id, session_token_entry.id)
            self.assertIsNone(refresh_token_entry.revoke_timestamp)

            self.assertEqual(session_entry.user_id, user.id)
            self.assertIsNone(session_entry.ip_address)
            self.assertTrue((dt.datetime.now() -  dt.datetime.fromtimestamp(float(session_entry.created_at))) < dt.timedelta(minutes=1))
            self.assertTrue((dt.datetime.now() -  dt.datetime.fromtimestamp(float(session_entry.last_active_at))) < dt.timedelta(minutes=1))
            self.assertTrue((dt.datetime.now() + dt.timedelta(seconds=conf.api.session_validity) -  dt.datetime.fromtimestamp(float(session_entry.expiration_timestamp))) < dt.timedelta(minutes=1))        

    def test_generate_new_session_with_valid_ip_address(self):
        with self.flask_application.app.app_context():
            user = db.session.query(UserModel).filter_by(id=self.user_id).one()
            ip_address = "1.1.1.1"
            session_token, refresh_token = utils.generate_new_session(user=user, ip_address=ip_address)
            refresh_token_hashed = sha256(refresh_token.encode('utf-8')).hexdigest()

            self.assertIsInstance(session_token, str)
            self.assertIsInstance(refresh_token, str)
            session_token_entry = db.session.query(SessionTokenModel).filter_by(token=session_token).one()
            refresh_token_entry = db.session.query(RefreshTokenModel).filter_by(hashed_token=refresh_token_hashed).one()
            session_entry = db.session.query(SessionModel).filter_by(id=session_token_entry.session_id).one()

            self.assertIsNotNone(session_token_entry)
            self.assertIsNotNone(refresh_token_entry)
            self.assertIsNotNone(session_entry)

            self.assertEqual(session_entry.ip_address, ip_address)
            self.assertEqual(session_entry.user_id, user.id)        

    def test_generate_new_session_with_valid_ipv6_address(self):
        with self.flask_application.app.app_context():
            user = db.session.query(UserModel).filter_by(id=self.user_id).one()
            ip_address = "2001:4860:4860:0:0:0:0:8888"
            session_token, refresh_token = utils.generate_new_session(user=user, ip_address=ip_address)
            refresh_token_hashed = sha256(refresh_token.encode('utf-8')).hexdigest()

            self.assertIsInstance(session_token, str)
            self.assertIsInstance(refresh_token, str)
            session_token_entry = db.session.query(SessionTokenModel).filter_by(token=session_token).one()
            refresh_token_entry = db.session.query(RefreshTokenModel).filter_by(hashed_token=refresh_token_hashed).one()
            session_entry = db.session.query(SessionModel).filter_by(id=session_token_entry.session_id).one()

            self.assertIsNotNone(session_token_entry)
            self.assertIsNotNone(refresh_token_entry)
            self.assertIsNotNone(session_entry)

            self.assertEqual(session_entry.ip_address, ip_address)
            self.assertEqual(session_entry.user_id, user.id)   
    
    def test_generate_new_session_with_private_ip_address(self):
        with self.flask_application.app.app_context():
            user = db.session.query(UserModel).filter_by(id=self.user_id).one()
            ip_address = "192.168.1.1"
            session_token, refresh_token = utils.generate_new_session(user=user, ip_address=ip_address)
            refresh_token_hashed = sha256(refresh_token.encode('utf-8')).hexdigest()

            self.assertIsInstance(session_token, str)
            self.assertIsInstance(refresh_token, str)
            session_token_entry = db.session.query(SessionTokenModel).filter_by(token=session_token).one()
            refresh_token_entry = db.session.query(RefreshTokenModel).filter_by(hashed_token=refresh_token_hashed).one()
            session_entry = db.session.query(SessionModel).filter_by(id=session_token_entry.session_id).one()

            self.assertIsNotNone(session_token_entry)
            self.assertIsNotNone(refresh_token_entry)
            self.assertIsNotNone(session_entry)

            self.assertIsNone(session_entry.ip_address)
            self.assertEqual(session_entry.user_id, user.id)

    def test_generate_new_session_with_invalid_ip_address(self):
        with self.flask_application.app.app_context():
            user = db.session.query(UserModel).filter_by(id=self.user_id).one()
            ip_address = "invalid_ip"
            session_token, refresh_token = utils.generate_new_session(user=user, ip_address=ip_address)
            refresh_token_hashed = sha256(refresh_token.encode('utf-8')).hexdigest()

            self.assertIsInstance(session_token, str)
            self.assertIsInstance(refresh_token, str)
            session_token_entry = db.session.query(SessionTokenModel).filter_by(token=session_token).one()
            refresh_token_entry = db.session.query(RefreshTokenModel).filter_by(hashed_token=refresh_token_hashed).one()
            session_entry = db.session.query(SessionModel).filter_by(id=session_token_entry.session_id).one()

            self.assertIsNotNone(session_token_entry)
            self.assertIsNotNone(refresh_token_entry)
            self.assertIsNotNone(session_entry)

            self.assertIsNone(session_entry.ip_address)
            self.assertEqual(session_entry.user_id, user.id)
    
    def test_generate_new_session_with_empty_ip_address(self):
        with self.flask_application.app.app_context():
            user = db.session.query(UserModel).filter_by(id=self.user_id).one()
            ip_address = ""
            session_token, refresh_token = utils.generate_new_session(user=user, ip_address=ip_address)
            refresh_token_hashed = sha256(refresh_token.encode('utf-8')).hexdigest()

            self.assertIsInstance(session_token, str)
            self.assertIsInstance(refresh_token, str)
            session_token_entry = db.session.query(SessionTokenModel).filter_by(token=session_token).one()
            refresh_token_entry = db.session.query(RefreshTokenModel).filter_by(hashed_token=refresh_token_hashed).one()
            session_entry = db.session.query(SessionModel).filter_by(id=session_token_entry.session_id).one()

            self.assertIsNotNone(session_token_entry)
            self.assertIsNotNone(refresh_token_entry)
            self.assertIsNotNone(session_entry)

            self.assertIsNone(session_entry.ip_address)
            self.assertEqual(session_entry.user_id, user.id)

    def test_generate_multiple_sessions_same_user_unique_tokens(self):
        with self.flask_application.app.app_context():
            user = db.session.query(UserModel).filter_by(id=self.user_id).one()
            sessions = set()
            refresh_tokens = set()
            for _ in range(10):
                session_token, refresh_token = utils.generate_new_session(user=user, ip_address=None)
                sessions.add(session_token)
                refresh_tokens.add(refresh_token)
            self.assertEqual(len(sessions), 10)
            self.assertEqual(len(refresh_tokens), 10)

            user_sessions = db.session.query(SessionModel).filter_by(user_id=user.id).all()
            user_sessions_tokens = db.session.query(SessionTokenModel).filter_by(user_id=user.id).all()
            user_refresh_tokens = db.session.query(RefreshTokenModel).filter_by(user_id=user.id).all()
            self.assertEqual(len(user_sessions), 10)
            self.assertEqual(len(user_refresh_tokens), 10)

