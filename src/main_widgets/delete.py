from textual.containers import Vertical, Horizontal
from textual.widgets import Input, Button, Static
from textual.screen import ModalScreen
from textual.app import ComposeResult


from model.register_model import Profile
from model.register_model import EntryAlreadyExist
from model.record import Record


class VerticalEntries(Vertical):
    def __init__(self, profile: Profile) -> None:
        self.profile = profile
        super().__init__()
    
    def compose(self) -> ComposeResult:
        yield Static("Are you sure you want to delete your account? Type in your master password to confirm.")
        yield Input(placeholder="Password", password=True, id = "pword")
        yield Static(id="info")
        with Horizontal():
            yield Button("Cancel", id="cancel")
            yield Button("Delete account", id="submit", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            result = self.profile.verify_password(self.query_one(Input).value)
            
            if not result:
                self.query_one("#info", Static).update("Wrong password entered")
                return
            else:
                self.profile.delete_account()
                self.screen.dismiss(True)

        elif event.button.id == "cancel":
            self.screen.dismiss(False)

class DeleteAccountScreen(ModalScreen):
    """
    Screen when deleting account
    """
    BINDINGS = [
        ("ctrl+b", "app.pop_screen", "Pop screen")
    ]

    def __init__(self, profile: Profile):
        self.profile = profile
        super().__init__()

    def compose(self) -> ComposeResult:
        yield VerticalEntries(self.profile)