from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Button


class ConfirmScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Are you sure you want to delete this entry?")
            with Horizontal():
                yield Button("Cancel", id="cancel")
                yield Button("Delete", variant="error", id="delete")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "delete":
            self.dismiss(True)
        else:
            self.dismiss(False)
