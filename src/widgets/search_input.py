from textual.widgets import Input

class SearchInput(Input):
    def __init__(self):
        super().__init__(
            placeholder = "Search",
            select_on_focus = False
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Posts a Fuzzied message
        """
        from widgets.data_table import MyTable
        
        self.post_message(MyTable.Fuzzied(event.value))
