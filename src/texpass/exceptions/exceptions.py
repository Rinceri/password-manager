class EntryAlreadyExists(Exception):
    pass

class UsernameAlreadyExists(Exception):
    pass

class UsernameDoesNotExist(Exception):
    pass

class WrongPassword(Exception):
    pass

class InvalidArguments(Exception):
    pass

# drive sync exceptions
class DriveException(Exception):
    pass

class FolderNotFound(Exception):
    pass

class DatabaseNotFound(Exception):
    pass