import google.oauth2.credentials
import google_auth_oauthlib.flow
from environment import conf
from environment import logging
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime
from googleapiclient.http import MediaFileUpload
import tempfile
import json
from base64 import  b64decode
from Utils import utils
from database.google_drive_integration_repo import GoogleDriveIntegration as GoogleDriveIntegrationDB
import requests

FOLDER_NAME = "Zero-TOTP Backup"



def get_drive_service(credentials):
     try:
        dat_obj = datetime.strptime(credentials["expiry"], '%Y-%m-%d %H:%M:%S.%f')
        credentials["expiry"] = dat_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
     except:
          pass
     creds = Credentials.from_authorized_user_info(credentials)
     drive = build('drive', 'v3', credentials=creds)
     return drive

def backup(credentials, vault):
        drive = get_drive_service(credentials)
        folder = get_folder(FOLDER_NAME, drive)
        if folder == None:
            create_folder(FOLDER_NAME, drive)
            folder = get_folder(FOLDER_NAME, drive)
            if folder == None:
                logging.error("Error while creating the backup folder")
                raise Exception("Error while creating the backup folder")
        now = datetime.utcnow()
        now_str = now.strftime('%d-%m-%Y-%H-%M-%S')

        file = create_file(name=f"{now_str}_backup", drive=drive, content=vault, folder_id=folder.get("id"))
        return file
            
           
      


def get_folder(name, drive):
    result = drive.files().list(q=f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder'", fields="files").execute()
    if len(result.get('files')) == 0:
        return None
    elif len(result.get('files')) == 1:
          if result.get('files')[0].get('explicitlyTrashed'):
              return None
          else:
            return result.get('files')[0]
    else : 
          for folder in result.get('files'):
              if folder.get('name') == name and not folder.get('explicitlyTrashed'):
                  return folder
          return None

def create_folder(name, drive):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    return drive.files().create(body=file_metadata).execute()

def create_file(name, drive, content, folder_id= None):
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
     
def get_files_from_folder(folder_id, drive):
    result = drive.files().list(q = "'" + folder_id + "' in parents", fields="files" ).execute()
    not_trashed_files = []
    for file in result.get('files'):
        if not file.get('explicitlyTrashed'):
            not_trashed_files.append(file)
    return not_trashed_files

def get_last_backup_file(drive)-> (any, datetime):
    folder = get_folder(FOLDER_NAME, drive)
    if folder == None:
        raise utils.FileNotFound("No backup file found")
    result = get_files_from_folder(folder.get('id'), drive)
    if len(result) == 0:
        logging.debug("No backup file found in the drive")
        raise utils.FileNotFound("No backup file found")
    else : 
          return utils.extract_last_backup_from_list(result)

def get_last_backup_checksum(creds):
    drive = get_drive_service(creds)
    file, date = get_last_backup_file(drive)
    try:
        data_b64 = drive.files().get_media(fileId=file.get("id")).execute().decode("utf-8").split(",")[0]
        data = json.loads(b64decode(data_b64).decode("utf-8"))
        if "secrets_sha256sum" in data:
            return data["secrets_sha256sum"], date
        else:
            logging.error("No checksum found in the backup file")
            raise utils.CorruptedFile("No checksum found in the backup file")
    except Exception as e:
        logging.error("Error while decoding the backup file : " + str(e))
        raise utils.CorruptedFile("Error while decoding the backup file : " + str(e))


def clean_backup_retention(credentials, user_id) -> bool:
    logging.info("Cleaning backup retention for user " + str(user_id) + " ...")
    google_drive_integration_db = GoogleDriveIntegrationDB()
    last_backup_clean_date = google_drive_integration_db.get_last_backup_clean_date(user_id)
    if last_backup_clean_date is not None:
         date = datetime.strptime(last_backup_clean_date, '%Y-%m-%d')
         if (datetime.utcnow() - date).days < 1:
                logging.info("Backup retention already cleaned today")
                return True
    MINIMUM_NB_BACKUP = 20
    MAXIMUM_BACKUP_AGE = 30
    drive = get_drive_service(credentials)
    folder = get_folder(FOLDER_NAME, drive)
    if folder == None:
        logging.info("No backup to clean (no backup folder)")
        google_drive_integration_db.update_last_backup_clean_date(user_id, datetime.utcnow().strftime('%Y-%m-%d'))
        return True
    result = get_files_from_folder(folder.get('id'), drive)
    logging.debug("Found " + str(len(result)) + " backups")
    if len(result) <= MINIMUM_NB_BACKUP or len(result) == 0:
        logging.info("No backup to clean (too few backups)")
        google_drive_integration_db.update_last_backup_clean_date(user_id, datetime.utcnow().strftime('%Y-%m-%d'))
        return True
    else :
        logging.info("Looking for backups to clean")
        try:
            sorted_files = sorted(result, key=lambda x:  datetime.strptime(x.get("name").split("_")[0], '%d-%m-%Y-%H-%M-%S'))
            logging.info("Found " + str(len(sorted_files)) + " backups")
        except Exception as e:
             logging.info("Error while sorting backup files : " + str(e))
             google_drive_integration_db.update_last_backup_clean_date(user_id, datetime.utcnow().strftime('%Y-%m-%d'))
             return False
        for file in sorted_files[:-MINIMUM_NB_BACKUP]:
            date_str = file.get("name").split("_")[0]
            date = datetime.strptime(date_str, '%d-%m-%Y-%H-%M-%S')
            logging.debug('Inspecting backup file ' + file.get("name") + " created on " + date_str + ". Age : " + str((datetime.utcnow() - date).days) + " days")

            if (datetime.utcnow() - date).days > MAXIMUM_BACKUP_AGE:
                logging.info("Deleting backup file " + file.get("name"))
                body_value = {'trashed': True}
                drive.files().update(fileId=file.get("id"), body=body_value).execute()
        google_drive_integration_db.update_last_backup_clean_date(user_id, datetime.utcnow().strftime('%Y-%m-%d'))
        return True
    

def revoke_credentials(credentials): # pragma: no cover
    creds = google.oauth2.credentials.Credentials(**credentials)
    revoke = requests.post('https://oauth2.googleapis.com/revoke',
        params={'token': creds.token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})
    status_code = getattr(revoke, 'status_code')
    logging.info("Revoke status code : " + str(status_code))
    if status_code == 200:
        return True
    else:
        return False

def delete_all_backups(credentials):
    drive = get_drive_service(credentials)
    folder = get_folder(FOLDER_NAME, drive)
    if folder == None:
        return True
    result = get_files_from_folder(folder.get('id'), drive)
    for file in result:
        body_value = {'trashed': True}
        drive.files().update(fileId=file.get("id"), body=body_value).execute()
    return True
    