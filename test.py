import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
import webbrowser
import io

# need creds.json to work

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]


def main_test():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    webbrowser.register("brave", None, webbrowser.BackgroundBrowser("/usr/bin/brave"))

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "creds.json", SCOPES
            )
            creds = flow.run_local_server(port=0, browser="brave")
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)
        files = []
        page_token = None
        while True:
            # pylint: disable=maybe-no-member
            response = (
                service.files()
                .list(
                    pageSize = 10,
                    q="visibility = 'limited'",
                    spaces="drive",
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token,
                )
                .execute()
            )
            for file in response.get("files", []):
                # Process change
                print(f'Found file: {file.get("name")}, {file.get("id")}')
            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            # if page_token is None:
            break

    except HttpError as error:
        print(f"An error occurred: {error}")
        files = None

def main():
    webbrowser.register("brave", None, webbrowser.BackgroundBrowser("/usr/bin/brave"))

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "creds.json", SCOPES
            )
            creds = flow.run_local_server(port=0, browser="brave")
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    folder = get_folder(creds)
    print("Uploading to folder ", folder)

    upload_database(creds, [folder])

    fetch_database(creds, folder)
    

def overwrite_database(creds: Credentials, parent: str = None):
    """
    Overwrite the database if already exists
    """
    try:
        service = build("drive", "v3", credentials = creds)
        
        query = f"name = 'passwords.db' and trashed = false and '{parent}' in parents"
        result: dict = (
            service.files()
            .list(fields = "files(id)", q = query)
            .execute()
        )

        if not result.get('files'):
            print("Could not find anything")
            return False
    
        if os.path.exists('passwords.db'):
            media = MediaFileUpload("passwords.db")
        else:
            print("File does not exist, skipping...")
            return False
        service.files().update(fileId = result.get('files')[0]['id'], media_body = media).execute()

        print("Done!")
        return True
        

    except HttpError as error:
        print(f"error: {error}")



def upload_database(creds: Credentials, parents: list[str] = None):
    """
    Inserts passwords.db into a folder called "texpass" on Google Drive

    Ensure creds are loaded before calling this
    """

    if overwrite_database(creds, parents[0]):
        return

    try:
        service = build("drive", "v3", credentials = creds)
        
        file_metadata = {"name": "passwords.db", "parents": parents}
        if os.path.exists('passwords.db'):
            media = MediaFileUpload("passwords.db")
        else:
            print("File does not exist, skipping...")
            return False

        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"file id: {file.get("id")}")
        

    except HttpError as error:
        print(f"error: {error}")


def get_folder(creds: Credentials, name: str = "texpass") -> str:
    """
    Get file ID for the folder to save the passwords.db file to
    """
    try:
        service: Resource = build("drive", "v3", credentials=creds)
        
        # get a folder which is not shared with anyone or domain
        # make sure its not a trash folder
        results: dict = (
            service.files()
            .list(fields = "files(parents, id)", q = f"mimeType = 'application/vnd.google-apps.folder' and name = '{name}' and trashed = false")
            .execute()
        )

        folders = results.get("files")
        
        if not folders:
            print("No folder found.")
            return
        
        return folders[0]['id']
    
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


def fetch_database(creds: Credentials, parent: str):
    try:
        service = build("drive", "v3", credentials=creds)
        query = f"name = 'passwords.db' and trashed = false and '{parent}' in parents"
        result: dict = (
            service.files()
            .list(fields = "files(id)", q = query)
            .execute()
        )

        if not result.get('files'):
            print("No file exists. Upload before fetching")
            return
        else:
            fileId = result.get('files')[0]['id']
    
        results = service.files().get_media(fileId = fileId)
        file = io.BytesIO()

        downloader = MediaIoBaseDownload(file, results)
        done = False

        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}.")

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None
        return

    with open('passwords.db', 'wb') as test:
        test.write(file.getvalue())

    return file

if __name__ == "__main__":
  main()