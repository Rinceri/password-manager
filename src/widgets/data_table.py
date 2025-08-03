from textual.widgets import DataTable
from textual import events
from textual.message import Message
from textual.widgets.data_table import RowDoesNotExist

from screens.confirm import ConfirmScreen
from controller.table_controller import TableController
from helper.timed_string import TimeString
from widgets.search_input import SearchInput

class MyTable(DataTable):
    class Fuzzied(Message):
        """Posted when a fuzzy search happens"""
        def __init__(self, query: str) -> None:
            self.query = query
            super().__init__()

    BINDINGS = [
        ("ctrl+c", "copy", "Copy password"),
        ("right", "page_down", "Move one page down"),
        ("left", "page_up", "Move one page up"),
        ("ctrl+d", "delete_entry", "Delete entry")
    ]

    def __init__(self, controller: TableController):
        self.controller = controller
        self.digit_presses = TimeString(400 * 10**6)

        super().__init__(cursor_type="row")

    def add_columns(self):
        """
        Add this table's columns before filling table
        """
        super().add_columns(*self.controller.get_column_ordering())
        

    def fill_table(self):
        """
        Adds all DataTable rows. Requires a populated internal table

        Note that this does not clear the table or add columns
        """
        rows = self.controller.generate_rows()
        
        for row, key in rows:
            self.add_row(*row, key = key)

    def show_fuzzy_result(self, message: Fuzzied):
        """
        Update table records based on new fuzzy search

        If empty, shows all records
        """
        # clear table
        self.clear()

        # if query is not ""
        if message.query:
            fuzzied_records = self.controller.generate_fuzzied_rows(message.query)
        else:
            # since there is no search, display all records
            self.fill_table()
            return
        
        for record, key in fuzzied_records:
            self.add_row(*record, key = key)

    def add_new_row(self, id: int, website: str, username: str):
        """
        Use when adding new entry to the DataTable.
        
        Note that this does not commit to database. Use controller for that.
        """
        self.add_row(id, website, username, key = str(id))

    def action_copy(self) -> None:
        """
        Copy password at cursor row
        """
        try:
            _, website, username = self.get_row_at(self.cursor_row)
        except RowDoesNotExist:
            return
        
        self.controller.copy_password_at(username, website)
        self.notify("Password has been copied", title="Copy successful", timeout=3)

    def action_delete_entry(self) -> None:
        """Delete entry at cursor row"""
        try:
            _, website, username = self.get_row_at(self.cursor_row)
        except RowDoesNotExist:
            return

        def process_delete(confirmed: bool):
            if confirmed:
                # delete entry from database
                self.controller.delete_entry(username, website)
                # fill table from scratch
                self.clear()
                self.fill_table()
    
        # this currently works without screen_switcher as this is a simple true/false return
        self.app.push_screen(ConfirmScreen(), process_delete)

    def _on_key(self, event: events.Key):
        # move to a specific index
        # can move to double digit index cells within 400 ms
        if event.character in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            # rown as in row number
            id_key = self.digit_presses.send(event.character)

            # move cursor to final number
            try:
                # move to row index from ID (key)
                row_index = self.get_row_index(id_key)
                self.move_cursor(row = row_index)
            except RowDoesNotExist:
                pass
        # is a character, type it to Input
        elif event.is_printable:
            inp = self.parent.query_one("Input", SearchInput)
            inp.value += event.character
            # move cursor to end of input
            inp.action_cursor_right()
            # focus on input widget
            inp.focus()
