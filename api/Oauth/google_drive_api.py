import google.oauth2.credentials
import google_auth_oauthlib.flow
import environment as env
from environment import logging
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime
from googleapiclient.http import MediaFileUpload
import tempfile
import json
from base64 import  b64decode

FOLDER_NAME = "Zero-TOTP Backup"

class FileNotFound(Exception):
    pass
class CorruptedFile(Exception):
     pass


def get_drive_service(credentials):
     dat_obj = datetime.strptime(credentials["expiry"], '%Y-%m-%d %H:%M:%S.%f')
     credentials["expiry"] = dat_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
     creds = Credentials.from_authorized_user_info(credentials)
     drive = build('drive', 'v3', credentials=creds)
     return drive

def backup(credentials, vault):
        drive = get_drive_service(credentials)
        folder = get_folder(FOLDER_NAME, drive)
        if folder.get("id") is None or folder.get('explicitlyTrashed'):
             folder = create_folder(FOLDER_NAME, drive)
        now = datetime.now()
        now_str = now.strftime('%d-%m-%Y-%H-%M-%S')

        file = create_file(name=f"{now_str}_backup", drive=drive, content=vault, folder_id=folder.get("id"))
        return file
            
           
      


def get_folder(name, drive):
    result = drive.files().list(q=f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder'", fields="files").execute()
    if len(result.get('files')) == 0:
        return None
    elif len(result.get('files')) == 1:
          return result.get('files')[0]
    else : 
          for folder in result.get('files'):
              if folder.get('name') == name:
                  return folder

def create_folder(name, drive):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    return drive.files().create(body=file_metadata).execute()

def create_file(name, drive, content, folder_id=None):
     file_metadata = {
             'name': name,  
        }
     if folder_id is not None:     
            file_metadata['parents'] = [folder_id]
     with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(content.encode('utf-8'))
            tmp.seek(0)
            media = MediaFileUpload(tmp.name, mimetype='text/plain')
            file = drive.files().create(body=file_metadata, media_body=media).execute()
            return file

def get_last_backup_file(drive):
    folder = get_folder(FOLDER_NAME, drive)
    result = drive.files().list(q = "'" + folder.get('id') + "' in parents", fields="files" ).execute()
    if len(result.get('files')) == 0:
        raise FileNotFound("No backup file found")
    elif len(result.get('files')) == 1:
          return result.get('files')[0]
    else : 
          last_backup_file_date = None
          last_backup_file = None
          for file in result.get('files'):
              logging.info("name =" +file.get("name"))
              if "_backup" not in file.get("name") or file.get('explicitlyTrashed'):
                  continue
              date_str = file.get("name").split("_")[0]
              try:
                date = datetime.strptime(date_str, '%d-%m-%Y-%H-%M-%S')
              except Exception:
                    continue
              if last_backup_file_date is None:
                  last_backup_file_date = date
                  last_backup_file = file
              elif date > last_backup_file_date:
                    last_backup_file_date = date
                    last_backup_file = file
          if last_backup_file is None:
              raise FileNotFound("No backup file found")
          return last_backup_file,last_backup_file_date

def get_last_backup_checksum(creds):
    drive = get_drive_service(creds)
    file, date = get_last_backup_file(drive)
    try:
        data_b64 = drive.files().get_media(fileId=file.get("id")).execute().decode("utf-8").split(",")[0]
        logging.info("data_b64 = " + data_b64)
        data = json.loads(b64decode(data_b64).decode("utf-8"))
        if "secrets_sha256sum" in data:
            return data["secrets_sha256sum"], date
        else:
            logging.error("No checksum found in the backup file")
            raise CorruptedFile("No checksum found in the backup file")
    except Exception as e:
        logging.error("Error while decoding the backup file : " + str(e))
        raise CorruptedFile("Error while decoding the backup file : " + str(e))