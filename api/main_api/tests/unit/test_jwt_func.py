import jwt 
import unittest
from main_api.CryptoClasses.jwt_func import verify_jwt, generate_jwt
import datetime
from main_api.environment import conf
from connexion.exceptions import Forbidden


class TestJWT(unittest.TestCase):

    def setUp(self):
        self.timezone = datetime.timezone.utc
        self.timeFormat = "%Y-%m-%d %H:%M:%S"
        self.validPayload = {
            "iss": "https://api.zero-totp.com",
            "sub": 1,
            "iat": datetime.datetime.utcnow(),
            "nbf": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        }
        self.secret = conf.api.jwt_secret
        self.algorithm = "HS256"

    def test_verify_jwt_correct(self):
        validJWT = jwt.encode(self.validPayload, self.secret, algorithm=self.algorithm)
        data_verified = verify_jwt(validJWT)
        self.assertEqual(data_verified["sub"], 1)
        self.assertEqual("admin" not in data_verified, True)

    def test_verify_jwt_invalid_iss(self):
        self.validPayload["iss"] = "https://evil.com"
        validJWT = jwt.encode(self.validPayload, self.secret, algorithm=self.algorithm)
        self.assertRaises(Forbidden, verify_jwt, validJWT)
    
    def test_verify_jwt_invalid_iat(self):
        self.validPayload["iat"] = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        validJWT = jwt.encode(self.validPayload, self.secret, algorithm=self.algorithm)
        self.assertRaises(Forbidden, verify_jwt, validJWT)

    def test_verify_jwt_invalid_nbf(self):
        self.validPayload["nbf"] = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        validJWT = jwt.encode(self.validPayload, self.secret, algorithm=self.algorithm)
        self.assertRaises(Forbidden, verify_jwt, validJWT)
    

    def test_verify_jwt_invalid_exp(self):
        self.validPayload["exp"] = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        validJWT = jwt.encode(self.validPayload, self.secret, algorithm=self.algorithm)
        self.assertRaises(Forbidden, verify_jwt, validJWT)
    

    def test_verify_jwt_invalid_signature(self):
        self.secret = "anothersecret"
        validJWT = jwt.encode(self.validPayload, self.secret, algorithm=self.algorithm)
        self.assertRaises(Forbidden, verify_jwt, validJWT)

    

    def test_generate_jwt(self):
        jwt = generate_jwt(1)
        self.assertTrue(jwt)
        self.assertTrue(verify_jwt(jwt))
        self.assertEqual(verify_jwt(jwt)["sub"], 1)
        self.assertEqual("admin" not in verify_jwt(jwt), True)
    
    def test_generate_jwt_admin(self):
        jwt = generate_jwt(user_id=1, admin=True)
        self.assertTrue(jwt)
        self.assertTrue(verify_jwt(jwt))
        self.assertEqual(verify_jwt(jwt)["sub"], 1)
        self.assertEqual(verify_jwt(jwt)["admin"], 1)

    def test_generate_jwt_invalid_key(self):
        realSecret = conf.api.jwt_secret
        conf.api.jwt_secret = "-----BEGIN PUBLIC KEY-----\nMFswDQYJKoZIhvcNAQEBBQADSgAwRwJAQqbu/gXebwVHrK9DAh/yeMu7Hw7P0HC4sgwE88Kep51c/WDeAJsd9NHd5AM3Omq1f8A2SP6kPP5sC7kI7douswIDAQAB\n-----END PUBLIC KEY-----"
        self.assertRaises(Exception, generate_jwt, 1)
        conf.api.jwt_secret = realSecret
