import google.oauth2.credentials
import google_auth_oauthlib.flow
import environment as env
import logging
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime





def backup(credentials):
        dat_obj = datetime.strptime(credentials["expiry"], '%Y-%m-%d %H:%M:%S.%f')
        credentials["expiry"] = dat_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        creds = Credentials.from_authorized_user_info(credentials)
        drive = build('drive', 'v2', credentials=creds)
        #files = drive.files().list().execute()
