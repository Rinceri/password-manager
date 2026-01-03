# Texpass - Password Manager for the Terminal
[![PyPI](https://img.shields.io/pypi/v/texpass?label=PyPI)](https://pypi.org/project/texpass/)

Texpass is a password manager written in Python with a text-based user interface. It uses the Textual framework for the UI.

---

https://github.com/user-attachments/assets/5cf6b56f-1e5c-4e2c-95e1-23c0d765631a

### Security features
- Uses Argon2 hashing to store master password in database.
- Encryption keys are derived from the master password, and hence never stored in database.
- Can generate securely random passwords

### Installation
This is currently available as a CLI tool and as a TUI.

For the CLI version, please see the [v1.x branch](https://github.com/Rinceri/password-manager/tree/v1.x)

The most up-to-date and actively maintained version is the TUI version. Available on PyPI:
```sh
python3 -m pip install -U texpass 
```
And run with:
```sh
texpass
```
The application can be quit by pressing the escape key.

### Backup with Google Drive
The ability to backup your database has been added recently. **There are a couple pitfalls at the moment so use with caution.**

This only works with Google Drive at the moment. Follow the steps below to enable it:
1. Create a new Google Cloud project by following the steps [here](https://developers.google.com/workspace/guides/create-project#project).
2. Enable [Google Drive API](https://developers.google.com/workspace/drive/api/quickstart/python#enable_the_api)
3. Configure OAuth consent screen ([steps](https://developers.google.com/workspace/drive/api/quickstart/python#configure_the_oauth_consent_screen))
    - If following above steps, you may not be able to select "Internal" audience. Select "External" audience if that is the case.
    - Go to [Audience](https://console.cloud.google.com/auth/audience) for your project and in test users section, add a test user with the email you want to use for Drive backups
4. Authorize credentials for the application by following these [steps](https://developers.google.com/workspace/drive/api/quickstart/python#authorize_credentials_for_a_desktop_application)
    - Set application type to "desktop app".
    - Select "Download JSON" and name it to `creds.json`
5. Move this file to wherever you call texpass from in the command line
    - Let's say you call it from `/home/username/Documents/texpass/` (Linux) (if you have already used the app before you would notice a `passwords.db` file there), move it to that folder
6. Run the below command and follow the steps in there
```sh
python3 -m texpass --cloud
```
7. Create a folder named "texpass" in your Google Drive

Now when entering the application, using `Ctrl+S` allows you to either upload your database file to Drive under texpass folder, or download it from there.

**CAUTION: Since uploading/downloading overwrites the database file, make sure to upload after making changes, and download as soon as possible if changes were made on another device and uploaded to Drive, to avoid version conflicts/overwrites**

**CAUTION 2: creds.json and token.json files are secret files that should NEVER be shared and should be stored securely.**

These were the pitfalls. Future updates will work on enhancing the security and making the process easier/more automatic. 

### Contributing
Feel free to report any bugs or additional features.
