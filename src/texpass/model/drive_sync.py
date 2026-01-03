import os.path
import io

from google.auth.transport.requests import Request
from google.auth.credentials import TokenState
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

from texpass.exceptions.exceptions import DriveException, FolderNotFound, DatabaseNotFound
from texpass.helper.wsgi_server import LocalServer

class DriveSync:
    """
    Should only be instantiated through OAuthDrive
    """
    def __init__(self, creds: Credentials, parent_folder_name: str = "texpass"):
        self.creds = creds
        self.parent_name = parent_folder_name
        
        # NOTE may not work
        self.parent_id = self._get_parent_id()
    
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


class OAuthDrive:
    """
    Get DriveSync class using this
    
    Workflow:
    1. Check creds exist
    2. If they do, get drive instance
    3. If they don't, get flow url
    3.1. Run server to process auth flow
    3.2 Get drive instance
    """

    SCOPES = ["https://www.googleapis.com/auth/drive"]

    def __init__(self, access_token_file: str):
        self.access_file = access_token_file
        self.flow = None
        # since we use a local web server to listen for google auth server
        self.redirect_uri = "http://localhost:8080"
        self.creds = None

    def creds_exist(self) -> bool:
        """
        Returns True if access token exists and is valid. Otherwise returns false

        If valid, can successfully create DriveSync object
        """
        # check if access token exists
        if os.path.exists(self.access_file):
            self.creds = Credentials.from_authorized_user_file(self.access_file, OAuthDrive.SCOPES)
        else:
            return False

        if self.creds.token_state == TokenState.INVALID:
            # if invalid, and can be refreshed, attempt to refresh
            if self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except:
                    # attempt failed
                    return False
                else:
                    # write to creds file after refreshing
                    self._write_access_token_to_file()
                    return True
            return False

        # creds token state is valid
        return True
    
    def get_flow_url(self, auth_client_file: str) -> str:
        """
        Returns URL to authenticate client and get access token

        Local server has started running. Make sure to run_server after
        """
        self.flow = InstalledAppFlow.from_client_secrets_file(
            auth_client_file, OAuthDrive.SCOPES,
            redirect_uri = self.redirect_uri
        )

        self.local_server = LocalServer(self.flow)

        return self.local_server.get_auth_url()
    
    def run_server(self):
        """
        Runs local server to get oauth access token. Saves it internally

        Make sure to run get_flow_url before this to get a Flow object
        """
        self.creds = self.local_server.run_local_server()
        self._write_access_token_to_file()

    def _write_access_token_to_file(self):
        with open(self.access_file, "w") as token:
            token.write(self.creds.to_json())

    def get_drive_instance(self, parent_folder_name: str = "texpass") -> DriveSync:
        """
        Create DriveSync object. Make sure to have valid creds have been loaded
        """
        return DriveSync(self.creds, parent_folder_name)


if __name__ == "__main__":
    oauthdrive = OAuthDrive("token.json")

    if not oauthdrive.creds_exist():
        url = oauthdrive.get_flow_url("creds.json")
        print(url)
        oauthdrive.run_server()
    
    drive = oauthdrive.get_drive_instance()
    drive.fetch()
