import unittest
from CryptoClasses.hash_func import Bcrypt
from Utils.utils import check_email, sanitize_input

class TestBcrypt(unittest.TestCase):
    
    def setUp(self):
        pass

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
