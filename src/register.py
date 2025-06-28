from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import Input, Button, Static
from textual import on

from model import register_model

from table import TableScreen

class SubmitInput(Input):
    """
    Custom input class that has modified keybind where ENTER key  
    presses the button with class "submit" on the screen
    """
    BINDINGS = [("enter", "press_submit", "Presses button with class submit")]

    def action_press_submit(self):
        self.screen.query_one(".submit", Button).press()
        
class Register:
    def field_filled(self, value: str) -> bool:
        return value != ""
    
    def commit(self, username: str, password: str) -> None:
        pf = register_model.ProfileFactory()
        profile = pf.register_profile(username, password)

        return profile


class VerticalButtons(Vertical):
    """
    Vertical consisting of two buttons

    Additional keybinds up and down to focus on previous/next widget respectively
    """
    def __init__(self, msg_widget: Static):
        self.msg_widget = msg_widget
        super().__init__()
        
    BINDINGS = [
        ("up", "app.focus_previous", "Focus on previous widget"),
        ("down", "app.focus_next", "Focus on next widget")
    ]

    def __send_update(self, value: str):
        self.msg_widget.update(value)

    def compose(self) -> ComposeResult:
        yield Button("Register",id="register_button", classes="submit")
        yield Button("Back", id="back_button")

    @on(Button.Pressed, "#back_button")
    def on_back(self):
        # to prevent cycling import
        from password_manager.main import LoginScreen

        self.app.switch_screen(LoginScreen())

    @on(Button.Pressed, "#register_button")
    def on_register(self):
        reg_check = Register()
        username = ""
        first_password = ""

        for input_ in self.parent.query("SubmitInput").results(SubmitInput):
            # empty field check
            if not reg_check.field_filled(input_.value):
                self.__send_update(f"Please fill {input_.name} field")
                return

            # new_username checks
            if input_.id == "new_username":
                username = input_.value
                continue
            
            # password/repeat password check
            elif input_.id == "new_password":
                # save password for check later
                first_password = input_.value
                continue

            elif input_.id == "new_password_again":
                # check password match
                if first_password == input_.value:
                    break
                else:
                    self.__send_update("Passwords don't match")
                    return
        
        try:
            profile = reg_check.commit(username, first_password)
            self.__send_update("Account has been registered!")
            self.app.switch_screen(TableScreen(profile))
            
        except register_model.UsernameAlreadyExists:
            self.__send_update("Username already exists")


class RegisterWidget(Vertical):
        
    def compose(self) -> ComposeResult:
        # username submitInput widget
        username = SubmitInput(
            placeholder="Enter new username", 
            classes="input",
            max_length=100,
            id = "new_username",
            name = "username"
        )

        username.border_title = "Username"

        # password submitInput widget
        password = SubmitInput(
            placeholder="Enter new password", 
            password=True, 
            classes="input",
            id="new_password",
            name = "password"    
        )

        password.border_title = "Password"

        # retype password submitInput widget
        re_password = SubmitInput(
            placeholder="Enter password again", 
            password=True, 
            classes="input",
            id="new_password_again",
            name = "password"
        )

        re_password.border_title = "Re-enter Password"
        
        add_msg = Static(id = "additional_message")
        
        # yield it all
        yield username
        yield password
        yield re_password
        yield VerticalButtons(add_msg)
        yield add_msg


class RegisterScreen(Screen):
    """
    The login screen. First screen when opening the app
    """
    CSS_PATH = "register.tcss"
    def __init__(self):
        super().__init__(classes="center_screen")

    def compose(self) -> ComposeResult:
        register_widget = RegisterWidget()
        register_widget.border_title = "Password Manager"
        yield register_widget
