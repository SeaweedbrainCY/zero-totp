import re
import html
from environment import logging
import datetime

class FileNotFound(Exception):
    pass

class CorruptedFile(Exception):
     pass

def check_email(email):
    email_regex = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    return re.match(email_regex, email) and re.search(email_regex, email).group() == email


def sanitize_input(string) -> str:
    string = string.replace("'", "")
    string = string.replace('"', "")
    return html.escape(string)

def get_all_secrets_sorted(totp_secrets_list):
    secrets = []
    for secret in totp_secrets_list:
        secrets.append({"uuid": secret.uuid, "enc_secret": secret.secret_enc})
    return sorted(secrets,key=lambda x: x["uuid"])

def extract_last_backup_from_list(files_list) -> (any, datetime):
    last_backup_file_date = None
    last_backup_file = None
    for file in files_list:
        logging.info("name =" +file.get("name"))
        if "_backup" not in file.get("name") or file.get('explicitlyTrashed'):
            continue
        date_str = file.get("name").split("_")[0]
        try:
          date = datetime.datetime.strptime(date_str, '%d-%m-%Y-%H-%M-%S')
        except Exception as e:
              logging.info("Error while parsing date : " + str(e) + " (file name : " + file.get("name") + ". Ignoring this file")
              continue
        if last_backup_file_date is None:
            last_backup_file_date = date
            last_backup_file = file
        elif date > last_backup_file_date:
              last_backup_file_date = date
              last_backup_file = file
    if last_backup_file is None:
        logging.info("No backup file found in the drive (last_backup_file is None)")
        raise FileNotFound("No backup file found")
    return last_backup_file,last_backup_file_date