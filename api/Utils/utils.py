import re
import html

def check_email(email):
    forbidden = '["\'<>]'
    return re.match(r'\S+@\S+\.\S+', email) and not re.search(forbidden, email)

def check_password(password):
   forbidden = '["\'<>]'
   return  not re.search(forbidden, password) 

def check_username(username):
    forbidden = '["\'<>]'
    return not re.search(forbidden, username)

def escape(string):
    string = string.replace("'", "")
    string = string.replace('"', "")
    return html.escape(string)