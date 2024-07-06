import unittest
from main_api.CryptoClasses.hash_func import Bcrypt
from main_api.Utils.utils import check_email, sanitize_input, extract_last_backup_from_list, FileNotFound, get_all_secrets_sorted, generate_new_email_verification_token, get_geolocation, send_information_email, get_ip
import datetime
from uuid import uuid4
from random import shuffle
from db_models.model import TOTP_secret
from unittest.mock import patch
import logging

class TestBcrypt(unittest.TestCase):
    
    def setUp(self):
        self.delete_email_token = patch("database.email_verification_repo.EmailVerificationToken.delete").start()
        self.delete_email_token.return_value = True

        self.add_email_token = patch("database.email_verification_repo.EmailVerificationToken.add").start()
        self.add_email_token.return_value = True
    
    def tearDown(self):
        patch.stopall()

#####################
### check_email tests
#####################
    def test_valid_emails_validation(self):
        valid_emails = [
            "user@example.com",
            "john.doe123@example.co.uk",
            "first_name.last_name@subdomain.example.org",
            "user_name@example.travel",
            "user123@example.museum",
            "admin@example.net",
            "test.email@example.com",
            "info@website.co",
            "contact@site.org",
            "user1234@sub.example",
            "user@domain.c",
            "user@example.c1ty",
            "user@domain.c1",
        ]
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(check_email(email), f"Email '{email}' should be valid")

    
    def test_invalid_emails(self):
        invalid_emails = [
            "invalid_email",
            "user@.com",
            "@example.com",
            "user@example.",
            "user@example com",
            "user@.co.uk",
            "user@.city",
        ]
        for email in invalid_emails:
            with self.subTest(email=email):
                self.assertFalse(check_email(email), f"Email '{email}' should be invalid")

    def test_email_attacks(self):
        attack_emails = [
            "user@example.com; attacker@example.com",
            "user@example.com; --sql-injection",
            "user@example.com; <script>alert('XSS')</script>",
            "admin@example.com; SELECT * FROM users;",
            "user@example.com; DROP TABLE users;",
            "user@example.com; DELETE FROM users;",
            "user@example.com; UNION SELECT password FROM users;",
            "user@example.com; OR '1'='1'; --",
        ]
        for email  in attack_emails:
            with self.subTest(email=email):
                self.assertFalse(check_email(email), f"Email '{email}' should not pass the check")
    

    def test_email_too_long(self):
        email = "a"*321 + "@example.com"
        self.assertFalse(check_email(email), f"Email '{email}' should be invalid")
    
#####################
###### sanitize tests
#####################
    def test_sanitize_plain_text(self):
        input_data = "This is plain text."
        sanitized = sanitize_input(input_data)
        self.assertEqual(sanitized, "This is plain text.")

    def test_sanitize_html_tags(self):
        input_data = "<div>Some <strong>text</strong></div>"
        sanitized = sanitize_input(input_data)
        self.assertEqual(sanitized, "&lt;div&gt;Some &lt;strong&gt;text&lt;/strong&gt;&lt;/div&gt;")

    def test_sanitize_script_tag(self):
        input_data = "<script>alert('XSS');</script>"
        sanitized = sanitize_input(input_data)
        self.assertEqual(sanitized, "&lt;script&gt;alert(XSS);&lt;/script&gt;")

    def test_sanitize_dangerous_attribute(self):
        input_data = '<a href="javascript:alert(\'XSS\')">Click me</a>'
        sanitized = sanitize_input(input_data)
        self.assertEqual(sanitized, '&lt;a href=javascript:alert(XSS)&gt;Click me&lt;/a&gt;')

    def test_sanitize_nested_tags(self):
        input_data = '<p><strong>Nested <a href="https://example.com">link</a></strong></p>'
        sanitized = sanitize_input(input_data)
        self.assertEqual(sanitized, '&lt;p&gt;&lt;strong&gt;Nested &lt;a href=https://example.com&gt;link&lt;/a&gt;&lt;/strong&gt;&lt;/p&gt;')

    def test_sanitize_ampersand(self):
        input_data = "This & That"
        sanitized = sanitize_input(input_data)
        self.assertEqual(sanitized, "This &amp; That")

    def test_sanitize_special_characters(self):
        input_data = "Less than < and greater than >"
        sanitized = sanitize_input(input_data)
        self.assertEqual(sanitized, "Less than &lt; and greater than &gt;")

    def test_sanitize_quotation_marks(self):
        input_data = 'Double quote " and single quote \''
        sanitized = sanitize_input(input_data)
        self.assertEqual(sanitized, 'Double quote  and single quote ')
    
################################
## extract_last_backup_from_list
################################


    def test_extract_last_backup_from_list(self):
        files = [
            {"name" : "06-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "15-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "02-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "03-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "04-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "05-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "12-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "07-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "08-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "16-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "10-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "11-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "01-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "13-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "14-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "18-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "17-01-2021-00-00-00_backup", "explicitlyTrashed": False},
        ]
        last_backup_file,last_backup_file_date = extract_last_backup_from_list(files)
        self.assertEqual(last_backup_file.get("name"), "18-01-2021-00-00-00_backup")
        self.assertEqual(last_backup_file_date, datetime.datetime(2021, 1, 18, 0, 0))
    
    def test_extract_last_backup_from_list_with_trashed_files(self):
        files = [
            {"name" : "06-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "15-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "02-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "03-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "04-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "05-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "12-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "07-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "08-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "16-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "10-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "11-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "01-01-2021-00-00-00_backup", "explicitlyTrashed": True},
            {"name" : "13-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "14-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "18-01-2021-00-00-00_backup", "explicitlyTrashed": True},
            {"name" : "17-01-2021-00-00-00_backup", "explicitlyTrashed": False},
        ]
        last_backup_file,last_backup_file_date = extract_last_backup_from_list(files)
        self.assertEqual(last_backup_file.get("name"), "17-01-2021-00-00-00_backup")
        self.assertEqual(last_backup_file_date, datetime.datetime(2021, 1, 17, 0, 0))
    
    def test_extract_last_backup_from_list_with_no_backup_files(self):
        files = []
        self.assertRaises(FileNotFound, extract_last_backup_from_list, files)

    
    def test_extract_last_backup_from_list_with_bad_file_name(self):
        files = [
            {"name" : "06-01-2021_00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "bad", "explicitlyTrashed": False},
            {"name" : "02-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "03-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "04-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "05-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "12-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "07-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "08-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "16-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "10-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "11-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "01-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "13-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "14-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "18-01-2021-00-00-00_backup", "explicitlyTrashed": False},
            {"name" : "17-01-2021-00-00-00_backup", "explicitlyTrashed": False},
        ]
        last_backup_file,last_backup_file_date = extract_last_backup_from_list(files)
        self.assertEqual(last_backup_file.get("name"), "18-01-2021-00-00-00_backup")
        self.assertEqual(last_backup_file_date, datetime.datetime(2021, 1, 18, 0, 0))

#########################
## get_all_secrets_sorted
#########################

    def test_get_all_secrets_sorted(self):
        secrets_uuid = []
        secrets = []
        for _ in range(0,50):
            secrets_uuid.append(str(uuid4()))
        secrets_uuid.sort()
        already_sorted_secrets = []
        for i in range(0,50):
            secrets.append(TOTP_secret(uuid=secrets_uuid[i], user_id=1, secret_enc="secret" ))
            already_sorted_secrets.append({"uuid": secrets_uuid[i], "enc_secret": "secret"})
        shuffle(secrets)
        secrets_sorted = get_all_secrets_sorted(secrets)
        self.assertEqual(secrets_sorted, already_sorted_secrets)



########################################
## generate_new_email_verification_token
########################################

    def test_generate_new_email_verification_token(self):
        token = generate_new_email_verification_token(1)
        self.delete_email_token.assert_called_once_with(1)
        self.add_email_token.assert_called_once()
        self.assertIsNotNone(token)

##################
## get_geolocation
##################

    def test_get_geolocation(self):
        ip = "1.1.1.1"
        geolocation = get_geolocation(ip)
        self.assertEqual(geolocation, "1.1.1.1 (4101 South Brisbane, Queensland, Australia)")
    
    def test_get_geolocation_with_private_ip(self):
        ip = "192.168.0.1"
        geolocation = get_geolocation(ip)
        self.assertEqual(geolocation, f"unknown (unknown, unknown)")
    

#########################
## send_information_email
#########################

    def test_send_information_email(self):
        get_geolocation_mock = patch("Utils.utils.get_geolocation").start()
        get_geolocation_mock.return_value = "IP"

        send_email_mock = patch("Utils.utils.send_email.send_information_email").start()
        send_email_mock.return_value = True

        send_information_email("IP", "email", "reason")
        get_geolocation_mock.assert_called_once_with("IP")
        send_email_mock.assert_called()


#########
## get_ip
#########
        
    def test_get_remote_ip(self):
        request = lambda:None
        request.remote_addr = "1.1.1.1"
        request.headers = {}
        ip = get_ip(request)
        self.assertEqual(ip, "1.1.1.1")

    def test_get_forwarded_for(self):
        request = lambda:None
        request.remote_addr = "192.168.0.0"
        request.headers = {"X-Forwarded-For": "1.1.1.1"}
        ip = get_ip(request)
        self.assertEqual(ip, "1.1.1.1")
    
    def test_get_no_ip(self):
        request = lambda:None
        request.remote_addr = "192.168.0.0"
        request.headers = {}
        ip = get_ip(request)
        self.assertIsNone(ip)
    
    def test_invalid_ip(self):
        request = lambda:None
        request.remote_addr = "testclient"
        request.headers = {}
        ip = get_ip(request)
        self.assertIsNone(ip)
