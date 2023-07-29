import re
import html

def check_email(email):
    forbidden = '["\'<>]'
    return re.match(r'\S+@\S+\.\S+', email) and not re.search(forbidden, email)

def check_password(password):
   forbidden = '["\'<>]'
   special = '[!@#$%^&*()_+\-=[\]{};:\\|,./?~]'
   upper = '[A-Z]'
   number = '[0-9]'
   return len(password) > 8 and len(password) <70 and re.search(special, password) and re.search(upper, password) and re.search(number, password) and not re.search(forbidden, password) 

def check_username(username):
    forbidden = '["\'<>]'
    return not re.search(forbidden, username)

def escape(string):
    string = string.replace("'", "")
    string = string.replace('"', "")
    return html.escape(string)