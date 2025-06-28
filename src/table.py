from textual.app import Screen, ComposeResult
from textual.widgets import DataTable, Footer, Input
from textual import events, fuzzy
from textual.message import Message
from textual.widgets.data_table import RowDoesNotExist

from time import time_ns

from main_widgets.create import NewEntryScreen
from main_widgets.confirm import ConfirmScreen
from main_widgets.delete import DeleteAccountScreen
from model.register_model import Profile
from model.record import Record


# TODO: make an add_row subcalssed method that takes first element and makes it key

class Data:
    """
    Helper class for DataTable
    """
    def __init__(self, profile: Profile):
        self.profile = profile
        self.all_records = []
    
    def make_table(self) -> DataTable:
        """
        Instantiate and populate a datatable
        """
        table = MyTable(self)
        records = self.profile.get_records()
        table.add_columns("ID", "Website", "Username")
        for i, record in enumerate(records, 1):
            row = (i, *record)
            table.add_row(*row, key = str(i))
            self.all_records.append(row)
        
        return table
    
    def remake_records(self, table: DataTable):
        records = self.profile.get_records()
        self.all_records = []

        for i, record in enumerate(records, 1):
            row = (i, *record)
            table.add_row(*row, key = str(i))
            self.all_records.append(row)
    
    def add_record(self, website: str, username: str) -> int:
        last = len(self.all_records) + 1
        self.all_records.append((last, website, username))

        return last
    
    def copy_password(self, website: str, username: str) -> None:
        """
        Copy password to clipboard for specific website/username
        """
        self.profile.copy_password_at(website, username)

    def delete_password(self, website: str, username: str) -> None:
        """
        Delete entry
        """
        self.profile.delete_password_at(website, username)



    def do_fuzzy(self, query: str) -> list[tuple[int, str, str], float]:
        """
        Do fuzzy search on all records

        Returns sorted by descending order
        """
        def make_string(row):
            """Make string for matching with query"""
            return " ".join([str(x) for x in row])
        
        result = []

        matcher = fuzzy.Matcher(query)
        
        for row in self.all_records:
            # get score
            score = matcher.match(make_string(row))
            # append to result list in the format ((id, website, username), score)
            result.append((row, score))
        
        # sort in descending order by score 
        return sorted(result, key = lambda x: x[-1], reverse = True)


class MyTable(DataTable):
    class Fuzzied(Message):
        """Posted when a fuzzy search happens"""
        def __init__(self, query: str) -> None:
            self.query = query
            super().__init__()

    class Inserted(Message):
        def __init__(self, website, username):
            self.website = website
            self.username = username
            super().__init__()


    BINDINGS = [
        ("ctrl+c", "copy", "Copy password"),
        ("right", "page_down", "Move one page down"),
        ("left", "page_up", "Move one page up"),
        ("ctrl+d", "delete_entry", "Delete entry")
    ]

    def __init__(self, data: Data):
        self.digit_presses = TimeString(400 * 10**6)

        self.data = data
        super().__init__(cursor_type="row")

    def action_copy(self) -> None:
        """Copy password at cursor row"""
        try:
            _, website, username = self.get_row_at(self.cursor_row)
        except RowDoesNotExist:
            return
        
        self.data.copy_password(website, username)
        self.notify("Password has been copied", title="Copy successful", timeout=3)

    def action_delete_entry(self) -> None:
        """Delete entry at cursor row"""
        try:
            _, website, username = self.get_row_at(self.cursor_row)
        except RowDoesNotExist:
            return

        def process_delete(ret: bool):
            if ret:
                self.data.delete_password(website, username)
                self.clear()
                self.data.remake_records(self)

        self.app.push_screen(ConfirmScreen(), process_delete)


    def _on_key(self, event: events.Key):
        # move to a specific index
        # can move to double digit index cells within 400 ms
        if event.character in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            # rown as in row number
            rown = self.digit_presses.send(event.character)

            # move cursor to final number
            try:
                # get row index from ID, which is key
                row_index = self.get_row_index(rown)
                # move cursor to this index
                self.move_cursor(row = row_index)
            except RowDoesNotExist:
                # eat 5 stars, do nothing
                pass
        # is a character, type it to Input
        elif event.is_printable:
            inp = self.parent.query_one("Input", MyInput)
            inp.value += event.character
            # move cursor to end of input
            inp.action_cursor_right()
            # focus on input widget
            inp.focus()


class TimeString:
    """
    Object that returns characters sent within a time chunk as a concatenated string

    Note that this does not return a string at the end of a time chunk, 
    but everytime a character is sent
    """
    def __init__(self, timeout_ns: int):
        self._final_str: str = ""
        self._start: int = time_ns()
        self._timed_out = True

        self._timeout = timeout_ns
    
    def __is_timeout(self) -> bool:
        return (time_ns() - self._start) > self._timeout
    
    def __refresh(self) -> None:
        self._start = time_ns()
        self._timed_out = False
        self._final_str = ""

    def send(self, char: str) -> str:
        """
        Send a character. Returns all characters since the start of time chunk
        """
        # checks if it has been 400+ ms since last send()
        if not self._timed_out:
            if self.__is_timeout():
                self._timed_out = True
            
        # if timed out, start fresh
        if self._timed_out:
            self.__refresh()

        # concatenate string-digits
        self._final_str += char
        
        return self._final_str


class MyInput(Input):
    def __init__(self):
        super().__init__(
            placeholder = "Search",
            select_on_focus = False
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        # post a fuzzy search
        self.post_message(MyTable.Fuzzied(event.value))


class TableScreen(Screen):

    CSS_PATH = "table.tcss"

    BINDINGS = [
        ("ctrl+e", "new_entry", "New entry"),
        ("escape", "logout", "Log out"),
        ("ctrl+delete", "delete_profile", "Delete profile")
    ]

    def __init__(self, profile: Profile):
        self.profile = profile
        self.data = Data(profile)
        self.table = None
        super().__init__()

    def compose(self) -> ComposeResult:
        self.table = self.data.make_table()
        yield MyInput()
        
        yield self.table
        yield Footer(show_command_palette=False)

    def on_my_table_fuzzied(self, message: MyTable.Fuzzied):
        # clear table
        self.table.clear()
        # if query is not ""
        if message.query:
            records = self.data.do_fuzzy(message.query)
        else:
            # since there is no search, display all records
            for record in self.data.all_records:
                self.table.add_row(*record, key = str(record[0]))
            return
        
        for record in records:
            # if search score better than nothing, display row
            if record[1] > 0:
                self.table.add_row(*record[0], key = str(record[0][0]))

    
    def action_new_entry(self) -> None:
        def add_record(record: Record):
            id = self.data.add_record(record.website, record.username)
            self.table.add_row(id, record.website, record.username, key = str(id))
        
        self.app.push_screen(NewEntryScreen(self.profile), add_record)

    def action_logout(self) -> None:
        from password_manager.main import LoginScreen
        self.app.switch_screen(LoginScreen())

    def action_delete_profile(self) -> None:
        def logout(status: bool):
            if status:
                self.action_logout()

        self.app.push_screen(DeleteAccountScreen(self.profile), logout)