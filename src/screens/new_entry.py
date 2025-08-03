from textual.containers import Vertical
from textual.widgets import Input, Button, Static
from textual.screen import ModalScreen
from textual.app import ComposeResult

from controller.table_controller import TableController
from exceptions.exceptions import EntryAlreadyExists

class NewEntryScreen(ModalScreen):
    """
    Screen when creating new password
    """
    BINDINGS = [
        ("ctrl+x", "app.pop_screen", "Pop screen")
    ]

    def __init__(self, controller: TableController):
        self.controller = controller
        super().__init__(id="new_modal")

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(placeholder="Username", id = "usname")
            yield Input(placeholder="Website", id = "webs")
            yield Input(value=self.controller.make_password(), placeholder="Password", id="pword", password=True)
            yield Static(id = "status")
            yield Button("Submit")

    def on_button_pressed(self) -> None:
        username = self.query_one("#usname").value
        website = self.query_one("#webs").value
        password = self.query_one("#pword").value
        
        if username == "" or website == "":
            self.query_one(Static).update("Please enter all fields")
            return
        
        try:
            id = self.controller.add_entry(username, website, password)
        except EntryAlreadyExists:
            self.query_one(Static).update("Entry already exists")
            return

        record = {"id": id, "website": website, "username": username}
        self.screen.dismiss(record)
