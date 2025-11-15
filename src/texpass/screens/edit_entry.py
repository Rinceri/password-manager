from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Static
from textual.screen import ModalScreen
from textual.app import ComposeResult

from texpass.controller.table_controller import TableController
from texpass.exceptions.exceptions import EntryAlreadyExists
from texpass.widgets.submit_input import SubmitInput

class EditEntryScreen(ModalScreen):
    """
    Screen when editing an entry
    """
    CSS_PATH = "../styles/modal_screens.tcss"
    BINDINGS = [
        ("escape", "app.pop_screen", "Pop screen")
    ]

    def __init__(self, controller: TableController, record_id: int, username: str, website: str, raw_password: str):
        self.controller = controller

        self.record_id = record_id
        self.username = username
        self.website = website
        self.raw_password = raw_password

        super().__init__(classes="centered", id="new_modal")

    def compose(self) -> ComposeResult:
        with Vertical(id="new_entry_vertical"):
            yield Static("Edit Entry")
            
            new_username = SubmitInput(value=self.username, placeholder="Username", id = "usname")
            new_username.border_title = "Username"
            
            new_website = SubmitInput(value=self.website ,placeholder="Website", id = "webs")
            new_website.border_title = "Website"

            new_password = SubmitInput(value=self.raw_password, placeholder="Password", id="pword", password=True)
            new_password.border_title = "Password"

            yield new_username
            yield new_website
            yield new_password
            yield Static(id = "status")
            with Horizontal():
                yield Button("Submit", classes = "submit")
                yield Button("Cancel", id = "cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()

        username = self.query_one("#usname").value
        website = self.query_one("#webs").value
        password = self.query_one("#pword").value
        
        if username == "" or website == "":
            self.query_one("#status", Static).update("Please enter all fields")
            return
        
        try:
            self.controller.edit_entry(self.record_id, username, website, password)
        except EntryAlreadyExists:
            self.query_one("#status", Static).update("Entry already exists")
            return

        record = {"edited": True, "website": website, "username": username}
        self.screen.dismiss(record)
