from texpass.model.drive_sync import OAuthDrive
import os.path


def main():
    ACCESS_FILE = "token.json"
    CREDS_FILE = "creds.json"

    if not os.path.exists(CREDS_FILE):
        print("ERROR: Cannot find file named creds.json")
        print("Follow the guide in the project's README to get client credentials to proceed")
        exit(1)
    
    auth = OAuthDrive(ACCESS_FILE)

    if auth.creds_exist():
        print("No changes made. All credentials are valid.")
        exit()
    
    # creds are invalid
    url = auth.get_flow_url(CREDS_FILE)

    print("=== Visit this link to authorize your account: ===")
    print(url)
    print("=== ===")

    auth.run_server()

    print("=== ===")
    print("Setup is complete. All credentials are valid.")
