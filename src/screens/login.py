from textual.app import ComposeResult
from textual.screen import Screen

from widgets.login import LoginWidget
from helper.switch_message import Switch
from controller.login import LoginController
from controller.screen_controller import ScreenController

class LoginScreen(Screen):
    """
    The login screen. First screen when opening the app
    """
    def __init__(self, controller: LoginController, switcher: ScreenController):
        self.controller = controller
        self.switcher = switcher
        super().__init__(classes="center_screen")

    def compose(self) -> ComposeResult:
        login_widget = LoginWidget(self.controller)
        login_widget.border_title = "Password Manager"
        yield login_widget

    def on_switch(self, message: Switch):
        if message.switch_else:
            self.switcher.to_register()
        else:
            self.switcher.to_table(message.account)
