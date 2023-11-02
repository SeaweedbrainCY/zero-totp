import google.oauth2.credentials
import google_auth_oauthlib.flow
import environment as env
import logging
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime
from googleapiclient.http import MediaFileUpload
import tempfile

FOLDER_NAME = "Zero-TOTP Backup"



def backup(credentials, vault):
        dat_obj = datetime.strptime(credentials["expiry"], '%Y-%m-%d %H:%M:%S.%f')
        credentials["expiry"] = dat_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        creds = Credentials.from_authorized_user_info(credentials)
        drive = build('drive', 'v3', credentials=creds)
        folder = get_folder(FOLDER_NAME, drive)
        if folder.get("id") is None or folder.get('explicitlyTrashed'):
             folder = create_folder(FOLDER_NAME, drive)
        now = datetime.now()
        now_str = now.strftime('%d-%m-%Y_%H-%M-%S')

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
             'name': name,  # Nom du fichier que vous souhaitez créer
        }
     if folder_id is not None:     
            file_metadata['parents'] = [folder_id]
     with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(content.encode('utf-8'))
            tmp.seek(0)
            media = MediaFileUpload(tmp.name, mimetype='text/plain')
            file = drive.files().create(body=file_metadata, media_body=media).execute()
            return file