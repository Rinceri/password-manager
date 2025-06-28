from textual.containers import Vertical
from textual.widgets import Input, Button, Static
from textual.screen import ModalScreen
from textual.app import ComposeResult

from model.register_model import Profile
from model.register_model import EntryAlreadyExist
from model.record import Record

from secrets import choice
from string import printable

class VerticalEntries(Vertical):
    def __init__(self, profile: Profile) -> None:
        self.profile = profile
        super().__init__(id="new_modal")
    
    def make_password(self) -> str:
        return ''.join(choice(printable) for _ in range(30))

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Username", id = "usname")
        yield Input(placeholder="Website", id = "webs")
        yield Input(value=self.make_password(),placeholder="Password", id="pword", password=True)
        yield Static(id = "status")
        yield Button("Submit")

    def on_button_pressed(self) -> None:
        uname = self.query_one("#usname").value
        webs = self.query_one("#webs").value
        pword = self.query_one("#pword").value
        
        if uname == "" or webs == "":
            self.query_one(Static).update("Please enter all fields")
            return
        
        ep = self.profile.encrypt_password(pword)

        try:
            self.profile.add_details(uname, webs, ep)
        except EntryAlreadyExist:
            self.query_one(Static).update("Entry already exists")
            return

        record = Record(webs, uname)
        self.screen.dismiss(record)

class NewEntryScreen(ModalScreen):
    """
    Screen when creating new password
    """
    BINDINGS = [
        ("ctrl+b", "app.pop_screen", "Pop screen")
    ]

    def __init__(self, profile: Profile):
        self.profile = profile
        super().__init__()

    def compose(self) -> ComposeResult:
        yield VerticalEntries(self.profile)