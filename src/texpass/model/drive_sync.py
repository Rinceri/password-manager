import os.path
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

from texpass.exceptions.exceptions import DriveException, FolderNotFound, DatabaseNotFound

class DriveSync:
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    def __init__(self, creds: Credentials, parent_folder_name: str = "texpass"):
        self.creds = creds
        self.parent_name = parent_folder_name
        
        # NOTE may not work
        self.parent_id = self._get_parent_id()
    
    @classmethod
    def from_oauth(cls, parent_folder_name: str = "texpass"):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", DriveSync.SCOPES)

        # If there are no (valid) credentials available, let the user log in using creds.json
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "creds.json", DriveSync.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return cls(creds, parent_folder_name)

    def _get_files(self):
        service = build("drive", "v3", credentials = self.creds)
        return service.files()
    
    def _get_file_list(self, query: str, fields: str = "files(id)") -> dict:
        return (
            self._get_files()
            .list(fields = fields, q = query)
            .execute()
        )

    def _get_parent_id(self) -> str:
        """
        Get file id for parent folder. Raises FolderNotFound if not found
        """
        # get a folder which is not shared with anyone or domain
        # make sure its not a trash folder
        query = f"mimeType = 'application/vnd.google-apps.folder' and name = '{self.parent_name}' and trashed = false"
        results = self._get_file_list(query)
        
        folders = results.get("files")

        # folders should contain a list of elements, if none, will evaluate to false
        if not folders:
            raise FolderNotFound(f"Folder with name {self.parent_name} could not be found")
        
        # get the first instance of the folder, and return its ID
        return folders[0]['id']

    def upload(self) -> str:
        """
        Inserts passwords.db into parent folder on Google Drive
        
        When successful, returns id of uploaded file
        """
        # check if passwords.db file exists locally
        if os.path.exists('passwords.db'):
            media = MediaFileUpload("passwords.db")
        else:
            raise DatabaseNotFound("File passwords.db was not found")

        try:
            try:
                fileId = self._get_cloud_save()
    
                # file exists in cloud, just overwrite it
                file = self._get_files().update(fileId = fileId, media_body = media, fields = 'id').execute()
            except DatabaseNotFound:
                # file doesn't exist, upload local to cloud
                file_metadata = {"name": "passwords.db", "parents": [self.parent_id]}
                file = self._get_files().create(body = file_metadata, media_body = media, fields = 'id').execute()
            
        except HttpError as e:
            raise DriveException(e)
        else:
            return file.get('id')

    def _get_cloud_save(self) -> str:
        """
        Get file id of passwords.db if it exists in cloud under parent folder and not in trash

        Raises DatabaseNotFound if not found
        """
        query = f"name = 'passwords.db' and trashed = false and '{self.parent_id}' in parents"
        files = self._get_file_list(query)

        if files.get('files'):
            return files.get('files')[0]['id']
        else:
            raise DatabaseNotFound("File passwords.db was not found in cloud")

    def fetch(self):
        """
        Download database from cloud, under parent folder and not in trash

        If not found, raises DatabaseNotFound
        """
        try:
            # if database not found, let it bubble up to the caller
            fileId = self._get_cloud_save()
            results = self._get_files().get_media(fileId = fileId)
            file = io.BytesIO()

            downloader = MediaIoBaseDownload(file, results)
            done = False

            while done is False:
                _, done = downloader.next_chunk()

        except HttpError as e:
            raise DriveException(e)
        
        # write to passwords.db file as bytes
        # should completely overwrite it if already exists
        with open('passwords.db', 'wb') as password_file:
            password_file.write(file.getvalue())


if __name__ == "__main__":
    drive = DriveSync.from_oauth()
    drive.fetch()
