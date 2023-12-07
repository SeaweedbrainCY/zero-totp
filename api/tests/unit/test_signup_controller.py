import unittest
import controllers
from app import app
from unittest.mock import patch
from database.model import User
import environment as env

class TestSignupController(unittest.TestCase):

    def setUp(self):
        if env.db_uri != "sqlite:///:memory:":
                raise Exception("Test must be run with in memory database")
        self.application = app
        self.client = self.application.test_client()


        self.getByEmailMocked = patch("database.user_repo.User.getByEmail").start()
        self.getByEmailMocked.return_value = False

        self.create_userMocked = patch("database.user_repo.User.create").start()
        self.create_userMocked.return_value = User(id=1)

        self.create_zkeMocked = patch("database.zke_repo.ZKE.create").start()
        self.create_zkeMocked.return_value = True

        self.delete_user = patch("database.user_repo.User.delete").start()
        self.delete_user.return_value = True

        self.hashpw = patch("CryptoClasses.hash_func.Bcrypt.hashpw").start()
        self.hashpw.return_value = "hashed"

        self.check_email = patch("Utils.utils.check_email").start()
        self.check_email.return_value = True 

        self.json_payload = {"username" : "username", "password": "Abcdefghij1#", "email": "test@test.py", "derivedKeySalt": "randomSalt", "ZKE_key": "encrypted_key", "passphraseSalt" :"randomSalt"}
        
        self.send_verification_email = patch("controllers.send_verification_email").start()
        self.send_verification_email.return_value = True

    def tearDown(self):
        patch.stopall()
        
    

    def test_signup(self):
        response = self.client.post("/signup", json=self.json_payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Set-Cookie", response.headers)
        self.assertIn("api-key", response.headers["Set-Cookie"])
        self.assertIn("HttpOnly", response.headers["Set-Cookie"])
        self.assertIn("Secure", response.headers["Set-Cookie"])
        self.assertIn("SameSite=Lax", response.headers["Set-Cookie"])
        self.assertIn("Expires", response.headers["Set-Cookie"])
        self.send_verification_email.assert_called_once()
    
    def test_signup_error_while_sending_verification_email(self):
        self.send_verification_email.side_effect = Exception("error")
        response = self.client.post("/signup", json=self.json_payload)
        self.assertEqual(response.status_code, 201)
    

    def test_signup_missing_parrameters(self):
        for key in self.json_payload.keys():
            json_payload = self.json_payload.copy()
            del json_payload[key]
            response = self.client.post("/signup", json=json_payload)
            self.assertEqual(response.status_code, 400)
        
        for key in self.json_payload.keys():
            json_payload = self.json_payload.copy()
            json_payload[key]=""
            response = self.client.post("/signup", json=json_payload)
            self.assertEqual(response.status_code, 400)
    
    def test_signup_forbidden_email(self):
        self.check_email.return_value = False 
        response = self.client.post("/signup", json=self.json_payload)
        self.assertEqual(response.status_code, 401)
    
    
    def test_signup_user_already_exists(self):
        self.getByEmailMocked.return_value = True 
        response = self.client.post("/signup", json=self.json_payload)
        self.assertEqual(response.status_code, 409)
    
    def test_signup_password_too_long(self):
        self.hashpw.side_effect = ValueError("Pass word too long")
        response = self.client.post("/signup", json=self.json_payload)
        self.assertEqual(response.status_code, 400)

    def test_signup_error_while_hashing(self):
        self.hashpw.side_effect = Exception("Unknown error")
        response = self.client.post("/signup", json=self.json_payload)
        self.assertEqual(response.status_code, 500)
    
    def test_signup_error_while_creating_user_1(self):
        self.create_userMocked.side_effect = Exception("error")
        response = self.client.post("/signup", json=self.json_payload)
        self.assertEqual(response.status_code, 500)
    
    def test_signup_error_while_creating_user_2(self):
        self.create_userMocked.return_value = False
        response = self.client.post("/signup", json=self.json_payload)
        self.assertEqual(response.status_code, 500)
    
    def test_signup_error_while_storing_zke(self):
        self.create_zkeMocked.side_effect = Exception("error")
        response = self.client.post("/signup", json=self.json_payload)
        self.assertEqual(response.status_code, 500)
        self.delete_user.assert_called()
    

   
    
    


    
    
