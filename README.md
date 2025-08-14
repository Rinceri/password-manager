# Dev branch for password manager

This is currently a work in progress for a better text based user interface.

The library used for making the UI is Textual.

This currently works, however you must have a DB file already generated (which is done by running `start.py`).

To run the app, run `main.py` from root directory (that is, run `src/main.py`)

Feel free to report any bugs or additional features.

TODO: update this to add an explanation on how the key derivation works (ie takes raw password, adds salt to it and gets key from its hash. This hash is different from login as login only uses raw password for hash)