import re
import html

def check_email(email):
    forbidden = '["\'<>&]'
    return re.match(r'\S+@\S+\.\S+', email) and not re.match(forbidden, email)

def check_password(password):
   forbidden = '["\'<>&]'
   special = '[!@#$%^&*()_+\-=[\]{};:\\|,./?~]'
   upper = '[A-Z]'
   number = '[0-9]'
   return len(password) < 8 or len(password) >70 or not re.match(special, password) or not re.match(upper, password) or not re.match(number, password) or re.match(forbidden, password) 

def check_username(username):
    forbidden = '["\'<>&]'
    return len(username) < 3 or len(username) > 20 or re.match(forbidden, username)

def escape(string):
    string = string.replace("'", "")
    string = string.replace('"', "")
    return html.escape(string)