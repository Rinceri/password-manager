from textual.containers import Vertical
from textual.widgets import Button, Static
from textual.screen import ModalScreen
from textual.app import ComposeResult

from texpass.model.drive_sync import DriveSync
from texpass.exceptions.exceptions import *


class SyncCloudScreen(ModalScreen):
    """
    Screen for syncing google drive database to local
    """
    CSS_PATH = "../styles/modal_screens.tcss"
    BINDINGS = [
        ("escape", "app.pop_screen", "Pop screen")
    ]

    def __init__(self):
        super().__init__(classes="centered", id="new_modal")

    def compose(self) -> ComposeResult:
        with Vertical(id="new_entry_vertical"):
            yield Static("Sync with Google Drive")
            yield Static(id = "status", classes="entrystatic")
            with Vertical():
                yield Button("Upload to Drive", id = "drive_upload", classes = "submit entrybutton")
                yield Button("Download from Drive", id = "drive_download", classes = "submit entrybutton")
                yield Button("Cancel", id = "cancel", classes = "entrybutton")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
            return
        try:
            drive = DriveSync.from_oauth()

            if event.button.id == "drive_upload":
                drive.upload()
                self.query_one("#status", Static).update("File has been uploaded under texpass folder")
                self.dismiss(False)
            elif event.button.id == "drive_download":
                drive.fetch()
                self.query_one("#status", Static).update("File has been downloaded.")
                self.dismiss(True)
        except Exception as e:
            self.query_one("#status", Static).update(f"An error occured: {e}")


# TODO
# handle errors