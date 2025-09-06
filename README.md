# Dev branch for password manager

This is currently a work in progress for a better text based user interface.

The library used for making the UI is Textual.

Try it out, this is currently deployed on testpypi:
```sh
$ pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple texpass==1.0.0
```
Note: I was testing quite a lot so there are versions above this but they are older. v1.0.0 is the latest.

And run with:
```sh
$ texpass
```
To quit application, ctrl + q

Feel free to report any bugs or additional features.

TODO: update this to add an explanation on how the key derivation works (ie takes raw password, adds salt to it and gets key from its hash. This hash is different from login as login only uses raw password for hash)
