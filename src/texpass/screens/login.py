from textual.app import ComposeResult
from textual.screen import Screen

from texpass.widgets.login import LoginWidget
from texpass.helper.switch_message import Switch
from texpass.controller.login import LoginController
from texpass.controller.screen_controller import ScreenController


class LoginScreen(Screen):
    """
    The login screen. First screen when opening the app
    """
    CSS_PATH = "../styles/login.tcss"

    def __init__(self, controller: LoginController, switcher: ScreenController):
        self.controller = controller
        self.switcher = switcher
        super().__init__(classes="centered first_screen")

    def compose(self) -> ComposeResult:
        login_widget = LoginWidget(self.controller)
        
        yield login_widget

    def on_switch(self, message: Switch):
        if message.switch_else:
            self.switcher.to_register()
        else:
            self.switcher.to_table(message.account)
