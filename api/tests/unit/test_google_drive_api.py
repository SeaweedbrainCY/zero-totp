import unittest
import environment as env
from unittest.mock import patch
from Oauth import google_drive_api  
import datetime
import Utils.utils as utils



class TestGoogleDriveAPI(unittest.TestCase):
        
        
        class MockedDriveService():
            mockedFiles = None
            def __init__(self, mockedFiles):
                self.mockedFiles= mockedFiles;
            
            def files(self):
                return self;
            def list(self, **kwargs):
                return self;
            def execute(self):
                  return self.mockedFiles;
            def create(self, **kwargs):
                    return self;

    
        def setUp(self):
            env.db_uri = "sqlite:///:memory:"
            self.from_authorized_user_info = patch("google.oauth2.credentials.Credentials.from_authorized_user_info").start()
            self.from_authorized_user_info.return_value = "credentials"
            self.build = patch("Oauth.google_drive_api.build").start()
            self.mockedFiles = {'files': []}
            self.drive = self.MockedDriveService(mockedFiles=self.mockedFiles)
            self.build.return_value = self.drive
        
        def tearDown(self):
          patch.stopall()
        
####################
## get_drive_service
####################
        
        def test_get_drive_service(self):
              credentials = {
                    "expiry" : "2021-01-01 00:00:00.000000",
              }
              self.assertEqual(google_drive_api.get_drive_service(credentials=credentials), self.drive)

        
        def test_get_drive_service_with_already_good_date(self):
                credentials = {
                        "expiry" : "2021-01-01T00:00:00Z",
                }
                self.assertEqual(google_drive_api.get_drive_service(credentials=credentials), self.drive)

#############
## get_folder
#############

        def test_get_folder(self):
                name = "myName"
                self.execute = patch("tests.unit.test_google_drive_api.TestGoogleDriveAPI.MockedDriveService.execute").start()
                self.execute.return_value = {
                    "files" : [
                        {
                            "name" : name, 
                            "explicitlyTrashed": False
                        }
                    ]
                }
                result = {
                    "files" : [
                        {
                            "name" : name,
                            "explicitlyTrashed": False
                        }
                    ]
                }
                self.assertEqual(google_drive_api.get_folder(name=name, drive=self.drive), result.get("files")[0])
        
        def test_get_folder_mutliple_folders(self):
                name = "myName"
                self.execute = patch("tests.unit.test_google_drive_api.TestGoogleDriveAPI.MockedDriveService.execute").start()
                self.execute.return_value = {
                    "files" : [
                        {
                            "name" : name, 
                            "explicitlyTrashed": False
                        }, 
                        {
                            "name": "otherName",
                            "explicitlyTrashed": False
                        }
                    ]
                }
                result = {
                    "files" : [
                        {
                            "name" : name,
                            "explicitlyTrashed": False
                        }
                    ]
                }
                self.assertEqual(google_drive_api.get_folder(name=name, drive=self.drive), result.get("files")[0])
        
        def test_get_folder_not_found(self):
                name = "myName"
                self.execute = patch("tests.unit.test_google_drive_api.TestGoogleDriveAPI.MockedDriveService.execute").start()
                self.execute.return_value = {
                    "files" : [
                        {
                            "name" : "anotherName", 
                            "explicitlyTrashed": False
                        }, 
                        {
                            "name": "otherName",
                            "explicitlyTrashed": False
                        }
                    ]
                }
                self.assertIsNone(google_drive_api.get_folder(name=name, drive=self.drive))

        def test_get_folder_no_folder(self):
                name = "myName"
                self.execute = patch("tests.unit.test_google_drive_api.TestGoogleDriveAPI.MockedDriveService.execute").start()
                self.execute.return_value = {
                    "files" : []
                }
                self.assertIsNone(google_drive_api.get_folder(name=name, drive=self.drive))
        
        def test_get_folder_trashed(self):
                name = "myName"
                self.execute = patch("tests.unit.test_google_drive_api.TestGoogleDriveAPI.MockedDriveService.execute").start()
                self.execute.return_value = {
                    "files" : [
                        {
                            "name" : name, 
                            "explicitlyTrashed": True
                        }, 
                        {
                            "name": "otherName",
                            "explicitlyTrashed": False
                        }
                    ]
                }
                self.assertIsNone(google_drive_api.get_folder(name=name, drive=self.drive))

################
## create_folder
################

        def test_create_folder(self):
               folder = {"id": 1, "name": "myFolder", "explicitlyTrashed": False}
               self.execute = patch("tests.unit.test_google_drive_api.TestGoogleDriveAPI.MockedDriveService.execute").start()
               self.execute.return_value = folder
               self.assertEqual(google_drive_api.create_folder(name="myFolder", drive=self.drive), folder)
               
################
## create_file
################

        def test_create_file(self):
               file = object()
               self.execute = patch("tests.unit.test_google_drive_api.TestGoogleDriveAPI.MockedDriveService.execute").start()
               self.execute.return_value = file
               self.assertEqual(google_drive_api.create_file(name="myFolder", content="test", drive=self.drive), file)
        
        def test_create_file_with_folder_id_not_existing(self):
               file = object()
               self.execute = patch("tests.unit.test_google_drive_api.TestGoogleDriveAPI.MockedDriveService.execute").start()
               self.execute.return_value = file
               self.assertEqual(google_drive_api.create_file(name="myFolder", content="test", drive=self.drive, folder_id=1), file)
       
        def test_create_file_with_folder_id_existing(self):
               file = object()
               self.execute = patch("tests.unit.test_google_drive_api.TestGoogleDriveAPI.MockedDriveService.execute").start()
               self.execute.return_value = file
               google_drive_api.create_folder(name="myFolder", drive=self.drive)
               self.assertEqual(google_drive_api.create_file(name="myFolder", content="test", drive=self.drive, folder_id=1), file)

#########
## backup
#########

        def test_backup(self):
             FOLDER_ID = 5
             VAULT = "vault"
             self.get_folder = patch("Oauth.google_drive_api.get_folder").start()
             self.get_folder.return_value = {"id" : FOLDER_ID}

             self.create_file = patch("Oauth.google_drive_api.create_file").start()  
             self.create_file.return_value = "file"
             
             self.assertEqual(google_drive_api.backup(credentials="creds", vault=VAULT), "file")
             self.create_file.assert_called_with(name=datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-%S')+"_backup", drive=self.drive, content=VAULT, folder_id=FOLDER_ID)
        
        def test_backup_with_folder_creation(self):
             VAULT = "vault"
             FOLDER_ID = 5
             def fake_create_foler(name, drive):
                 print("create foler")
                 files = {'files': [{"id" : FOLDER_ID, "name" :name, "explicitlyTrashed": False}]}
                 drive.mockedFiles =files
             create_file = patch("Oauth.google_drive_api.create_file").start()  
             create_file.return_value = "file"   
             create_folder = patch("Oauth.google_drive_api.create_folder").start()
             create_folder.side_effect = fake_create_foler
             


             
             self.assertEqual(google_drive_api.backup(credentials="creds", vault=VAULT), "file")
             create_file.assert_called_with(name=datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-%S')+"_backup", drive=self.drive, content=VAULT, folder_id=FOLDER_ID)

        def test_backup_with_folder_creation_error(self):
             VAULT = "vault"
             get_service = patch("Oauth.google_drive_api.get_drive_service").start()
             get_service.return_value = self.drive
             create_file = patch("Oauth.google_drive_api.create_file").start()  
             create_file.return_value = "file"
             create_folder = patch("Oauth.google_drive_api.create_folder").start()
             create_folder.return_value = {"id" : 1}
             execute = patch("tests.unit.test_google_drive_api.TestGoogleDriveAPI.MockedDriveService.execute").start()
             execute.return_value = {"files" : []}
             
             self.assertRaises(Exception, google_drive_api.backup, credentials="creds", vault=VAULT)

########################
## get_files_from_folder
########################

        def test_get_files_from_folder(self):
            FOLDER_ID = 5
            self.execute = patch("tests.unit.test_google_drive_api.TestGoogleDriveAPI.MockedDriveService.execute").start()
            self.execute.return_value = {
                "files" : [
                    {
                        "name" : "myName", 
                        "explicitlyTrashed": False
                    }, 
                    {
                        "name": "otherName",
                        "explicitlyTrashed": False
                    },
                    {
                        "name": "otherOtherName",
                        "explicitlyTrashed": True
                    }
                ]
            }
            result = {
                "files" : [
                    {
                        "name" : "myName", 
                        "explicitlyTrashed": False
                    }, 
                    {
                        "name": "otherName",
                        "explicitlyTrashed": False
                    },
                ]
            }
            self.assertEqual(google_drive_api.get_files_from_folder(folder_id=str(FOLDER_ID), drive=self.drive), result.get('files'))

#######################
## get_last_backup_file
#######################

       
    

        def test_get_last_backup_file(self):
            FOLDER_ID = 5
            LAST_BACKUP_FILENAME = "02-01-2023-00-00-00_backup"
            get_folder = patch("Oauth.google_drive_api.get_folder").start()
            get_folder.return_value = {"id" : str(FOLDER_ID)}
            execute = patch("tests.unit.test_google_drive_api.TestGoogleDriveAPI.MockedDriveService.execute").start()
            execute.return_value = {
                "files" : [
                    {
                        "name" : "01-01-2023-00-00-00_backup", 
                        "explicitlyTrashed": False
                    }, 
                    {
                        "name": LAST_BACKUP_FILENAME,
                        "explicitlyTrashed": False
                    },
                    {
                        "name": "03-01-2023-00-00-00_backup",
                        "explicitlyTrashed": True
                    }
                ]
            }
            self.assertEqual(google_drive_api.get_last_backup_file(drive=self.drive), ({"name" : LAST_BACKUP_FILENAME, "explicitlyTrashed": False}, datetime.datetime(year=2023, month=1, day=2, hour=0, minute=0, second=0 ) ))

        def test_get_last_backup_file_without_folder(self):
            get_folder = patch("Oauth.google_drive_api.get_folder").start()
            get_folder.return_value = None
            self.assertRaises(utils.FileNotFound, google_drive_api.get_last_backup_file, drive=self.drive)
        
        def test_get_last_backup_file_with_no_file(self):
            FOLDER_ID = 5
            get_folder = patch("Oauth.google_drive_api.get_folder").start()
            get_folder.return_value = {"id" : str(FOLDER_ID)}
            execute = patch("tests.unit.test_google_drive_api.TestGoogleDriveAPI.MockedDriveService.execute").start()
            execute.return_value = {"files": []}
            self.assertRaises(utils.FileNotFound, google_drive_api.get_last_backup_file, drive=self.drive)
        

        def test_get_last_backup_file_with_corrupted_file(self):
            FOLDER_ID = 5
            LAST_BACKUP_FILENAME = "02-01-2023-00-00-00_backup"
            get_folder = patch("Oauth.google_drive_api.get_folder").start()
            get_folder.return_value = {"id" : str(FOLDER_ID)}
            execute = patch("tests.unit.test_google_drive_api.TestGoogleDriveAPI.MockedDriveService.execute").start()
            execute.return_value = {
                "files" : [
                    {
                        "name" : "01-01-2023-00-00-00_backup", 
                        "explicitlyTrashed": False
                    }, 
                    {
                        "name": LAST_BACKUP_FILENAME,
                        "explicitlyTrashed": False
                    },
                    {
                        "name": "bad_filename",
                        "explicitlyTrashed": False
                    },
                    {
                        "name": "03-01-2023_00-00-00_backup",
                        "explicitlyTrashed": False
                    },
                    {
                        "name": "03-01-2023-00-00-00_backup",
                        "explicitlyTrashed": True
                    }
                ]
            }
            self.assertEqual(google_drive_api.get_last_backup_file(drive=self.drive), ({"name" : LAST_BACKUP_FILENAME, "explicitlyTrashed": False}, datetime.datetime(year=2023, month=1, day=2, hour=0, minute=0, second=0 ) ))
        
        def test_get_last_backup_file_with_all_files_trashed(self):
            FOLDER_ID = 5
            LAST_BACKUP_FILENAME = "02-01-2023-00-00-00_backup"
            get_folder = patch("Oauth.google_drive_api.get_folder").start()
            get_folder.return_value = {"id" : str(FOLDER_ID)}
            execute = patch("tests.unit.test_google_drive_api.TestGoogleDriveAPI.MockedDriveService.execute").start()
            execute.return_value = {
                "files" : [
                    {
                        "name" : "01-01-2023-00-00-00_backup", 
                        "explicitlyTrashed": True
                    }, 
                    {
                        "name": LAST_BACKUP_FILENAME,
                        "explicitlyTrashed": True
                    },
                    {
                        "name": "03-01-2023-00-00-00_backup",
                        "explicitlyTrashed": True
                    }
                ]
            }
            self.assertRaises(utils.FileNotFound, google_drive_api.get_last_backup_file, drive=self.drive)
    
        
###########################
## get_last_backup_checksum
###########################

        def test_get_last_backup_checksum(self):
            FOLDER_ID = 5
            LAST_BACKUP_FILENAME = "02-01-2023-00-00-00_backup"
            get_last_backup_file = patch("Oauth.google_drive_api.get_last_backup_file").start()
            get_last_backup_file.return_value = ({"name" : LAST_BACKUP_FILENAME, "explicitlyTrashed": False}, datetime.datetime(year=2023, month=1, day=2, hour=0, minute=0, second=0 ))
            self.assertEqual(google_drive_api.get_last_backup_checksum(drive=self.drive), LAST_BACKUP_FILENAME.split("_")[0])
            
        