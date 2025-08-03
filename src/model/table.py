from textual.fuzzy import Matcher

class Table:
    """
    Internal implementation of a table so it can be used to populate a Textual Datatable

    Note that indexing within this table starts from 1, for readability
    """
    def __init__(self):
        self.columns = ("ID", "Website", "Username")
        self.rows = []
    
    def populate_table(self, pg_records: list[tuple]):
        """
        Populates table from empty
        """
        self.rows = []

        for i, record in enumerate(pg_records, 1):
            self.rows.append((i, *record))

    def generator(self):
        """
        Returns a generator to iterate through when adding rows in table UI
        """
        for row in self.rows:
            yield row
    
    def get_key(self, row: tuple) -> str:
        # hardcoded ID column index
        return str(row[0])
    
    def get_fuzzied_records(self, query: str) -> list[tuple[tuple, int]]:
        """
        Do fuzzy search on all records

        Returns sorted by descending order, all scores greater than 0
        """
        def make_string(row):
            """Concatenate cells of a row as a string. For use in fuzzy matching"""
            return " ".join([str(cell) for cell in row])
        
        result = []

        matcher = Matcher(query)
        
        for row in self.rows:
            # get score
            score = matcher.match(make_string(row))

            if score > 0:
                # append to result list in the format ((id, website, username), score)
                # ... if score is higher than 0
                result.append((row, score))
            
        # sort in descending order by score
        return sorted(result, key = lambda x: x[-1], reverse = True)
    
    def add_record(self, website: str, username: str) -> int:
        """
        Appends new row to the table

        Returns ID of the new row
        """
        last = len(self.rows) + 1
        self.rows.append((last, website, username))

        return last