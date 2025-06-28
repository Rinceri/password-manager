from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import Button, Static
from textual import on

from register import RegisterScreen, SubmitInput
from model import register_model
from table import TableScreen, MyTable

class Login:
    def field_filled(self, value: str) -> bool:
        return value != ""
    
    def commit(self, username: str, password: str) -> None:
        pf = register_model.ProfileFactory()
        profile = pf.login_profile(username, password)

        return profile

class VerticalButtons(Vertical):
    def __init__(self, add_msg: Static):
        self.msg_widget = add_msg
        super().__init__()
    
    BINDINGS = [
        ("up", "app.focus_previous", "Focus on previous widget"),
        ("down", "app.focus_next", "Focus on next widget")
    ]

    def __send_update(self, value: str):
        self.msg_widget.update(value)

    def compose(self) -> ComposeResult:
        yield Button("Login",id="login_button", classes="submit")
        yield Button("Create account", id="register_button")
    

    @on(Button.Pressed, "#register_button")
    def on_register(self):
        self.app.switch_screen(RegisterScreen())

    @on(Button.Pressed, "#login_button")
    def on_login(self):
        prof_check = Login()
        username = ""
        password = ""

        for input_ in self.parent.query("SubmitInput").results(SubmitInput):
            # empty field check
            if not prof_check.field_filled(input_.value):
                self.__send_update(f"Please fill {input_.name} field")
                return

            # get username
            if input_.id == "username":
                username = input_.value
                continue
            
            # password
            elif input_.id == "inp_password":
                # save password for check later
                password = input_.value
                break
        
        try:
            profile = prof_check.commit(username, password)
            self.__send_update("You are being logged in...")
            self.app.switch_screen(TableScreen(profile))
        except register_model.UsernameDoesNotExist as e:
            self.__send_update("Username does not exist")
        except register_model.WrongPassword as e:
            self.__send_update("Wrong password")


class LoginWidget(Vertical):
    def compose(self) -> ComposeResult:
        username = SubmitInput(
            placeholder="Enter username", 
            classes="input", 
            id = "username",
            name = "username"
        )
        username.border_title = "Username"

        password = SubmitInput(
            placeholder="Enter password", 
            password=True, 
            classes="input",
            id="inp_password",
            name="password"
        )
        password.border_title = "Password"

        add_msg = Static(id = "additional_message")
        
        yield username
        yield password
        yield VerticalButtons(add_msg)
        yield add_msg


class LoginScreen(Screen):
    """
    The login screen. First screen when opening the app
    """
    def __init__(self):
        super().__init__(classes="center_screen")

    def compose(self) -> ComposeResult:
        login_widget = LoginWidget()
        login_widget.border_title = "Password Manager"
        yield login_widget


class MainApp(App):
    CSS_PATH = "main.tcss"

    def on_my_table_inserted(self, message: MyTable.Inserted):
        print("I GOT IT I GOT IT!")

    def on_mount(self):
        self.push_screen(LoginScreen())

if __name__ == "__main__":
    app = MainApp()
    app.run()
