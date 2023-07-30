import unittest
import controllers
from app import create_app
from unittest.mock import patch
from database.model import User
import environment as env

class TestControllers(unittest.TestCase):

    def setUp(self):
        env.db_uri = "sqlite:///:memory:"
        self.app = create_app()
        self.client = self.app.test_client()


        self.getByEmailMocked = patch("database.user_repo.User.getByEmail").start()
        self.getByEmailMocked.return_value = False

        self.create_userMocked = patch("database.user_repo.User.create").start()
        self.create_userMocked.return_value = User(id=1)

        self.create_zkeMocked = patch("database.zke_repo.ZKE.create").start()
        self.create_zkeMocked.return_value = True

        self.delete_user = patch("database.user_repo.User.delete").start()
        self.delete_user.return_value = True

        self.hashpw = patch("Crypto.hash_func.Bcrypt.hashpw").start()
        self.hashpw.return_value = "hashed"

        self.check_email = patch("Utils.utils.check_email").start()
        self.check_email.return_value = True 

        self.check_password = patch("Utils.utils.check_password").start()
        self.check_password.return_value = True

        self.check_username = patch("Utils.utils.check_username").start()
        self.check_username.return_value = True

        self.json_payload = {"username" : "username", "password": "Abcdefghij1#", "email": "test@test.py", "salt": "randomSalt", "ZKE_key": "encrypted_key"}

    def tearDown(self):
        patch.stopall()
        
    

    def test_signup(self):
        response = self.client.post("/signup", json=self.json_payload)
        self.assertEqual(response.status_code, 201)
    

    def test_signup_missing_parrameters(self):
        json_payload = {"password": "Abcdefghij1#", "email": "test@test.py", "salt": "randomSalt", "ZKE_key": "encrypted_key"}
        response = self.client.post("/signup", json=json_payload)
        self.assertEqual(response.status_code, 400)

        json_payload = {"username" : "username", "email": "test@test.py", "salt": "randomSalt", "ZKE_key": "encrypted_key"}
        response = self.client.post("/signup", json=json_payload)
        self.assertEqual(response.status_code, 400)

        json_payload = {"username" : "username", "password": "Abcdefghij1#", "salt": "randomSalt", "ZKE_key": "encrypted_key"}
        response = self.client.post("/signup", json=json_payload)
        self.assertEqual(response.status_code, 400)

        json_payload = {"username" : "username", "password": "Abcdefghij1#", "email": "test@test.py","ZKE_key": "encrypted_key"}
        response = self.client.post("/signup", json=json_payload)
        self.assertEqual(response.status_code, 400)

        json_payload = {"username" : "username", "password": "Abcdefghij1#", "email": "test@test.py", "salt": "randomSalt"}
        response = self.client.post("/signup", json=json_payload)
        self.assertEqual(response.status_code, 400)
    
    def test_signup_forbidden_email(self):
        self.check_email.return_value = False 
        response = self.client.post("/signup", json=self.json_payload)
        self.assertEqual(response.status_code, 403)
    
    def test_signup_forbidden_username(self):
        self.check_username.return_value = False 
        response = self.client.post("/signup", json=self.json_payload)
        self.assertEqual(response.status_code, 403)
    
    def test_signup_forbidden_password(self):
        self.check_password.return_value = False 
        response = self.client.post("/signup", json=self.json_payload)
        self.assertEqual(response.status_code, 403)
    
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
    

   
    
    


    
    
