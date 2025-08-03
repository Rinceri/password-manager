from helper.account import Account
from helper.status import Status
from exceptions.exceptions import UsernameDoesNotExist, WrongPassword


class LoginController:
    def log_in(self, username: str, password: str) -> Status:
        try:
            account = Account.from_login(username, password)
        except UsernameDoesNotExist:
            return Status(False, message="Username does not exist")
        except WrongPassword:
            return Status(False, message="Wrong Password")
        else:
            return Status(True, account=account, message="Logging you in...")
