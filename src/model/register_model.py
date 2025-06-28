import sqlite3
import argon2
from secrets import choice
import string
from cryptography.fernet import Fernet
import base64
import pyperclip

class Profile:
    def __init__(self, username: str, password: str, salt: str):
        self.account = username
        self.password = password
        self.salt = salt

    def __select_all_sql(self) -> str:
        return "SELECT website, username FROM passwords WHERE account_name = ?;"

    def __select_password_sql(self) -> str:
        return "SELECT encrypted_password FROM passwords \
            WHERE account_name = ? \
                AND username = ? \
                AND website = ?;"

    def __insert_password_sql(self) -> str:
        return "INSERT INTO passwords \
            (account_name, username, website, encrypted_password) \
            VALUES (?, ?, ?, ?)"

    def __remove_password_sql(self) -> str:
        return "DELETE FROM passwords \
            WHERE account_name = ? AND username = ? AND website = ?"

    def __make_con(self) -> sqlite3.Connection:
        return sqlite3.connect("passwords.db")
    
    def get_records(self) -> list[tuple]:
        con = self.__make_con()
        records = con.execute(self.__select_all_sql(), (self.account,))\
            .fetchall()
        con.close()

        return records
    
    def __get_hash(self) -> bytes:
        hashed_password = argon2.low_level.hash_secret(
            secret = self.password.encode(), 
            salt = self.salt.encode(), 
            time_cost = 3,
            memory_cost = 65536, 
            parallelism = 4, hash_len = 30, 
            type = argon2.Type.ID
        )

        return hashed_password[-32:]
    
    def __get_key(self) -> Fernet:
        return Fernet(base64.urlsafe_b64encode(self.__get_hash()))
    
    def __get_password_at(self, website: str, username: str) -> str:
        con = self.__make_con()
        enc_pass = con.execute(self.__select_password_sql(), (self.account, username, website))\
            .fetchone()\
                [0]
        con.close()

        password = self.__get_key().decrypt(enc_pass).decode()

        return password
    
    def copy_password_at(self, website: str, username: str) -> None:
        password = self.__get_password_at(website, username)

        pyperclip.copy(password)

    def delete_password_at(self, website: str, username: str) -> None:
        con = self.__make_con()
        with con:
            con.execute(
                self.__remove_password_sql(), (self.account, username, website)
            )
        
        con.close()
    
    def encrypt_password(self, password: str) -> bytes:
        key = self.__get_key()
        return key.encrypt(password.encode())
    
    def add_details(self, username: str, website: str, encrypted_password: bytes):
        con = self.__make_con()

        try:
            with con:
                con.execute(
                    self.__insert_password_sql(), 
                    (self.account, username, website, encrypted_password.decode())
                )
        except sqlite3.IntegrityError:
            con.close()
            raise EntryAlreadyExist()
        else:
            con.close()

    def __verify_hash(self, raw: str, hashed: str) -> bool:
        ph = argon2.PasswordHasher()
        
        return ph.verify(hashed, raw)

    def __make_select_statement(self) -> str:
        return "SELECT password_hash FROM user_login WHERE account_name = ?;"

    def verify_password(self, password: str) -> bool:
        con = sqlite3.connect("passwords.db")
        hash_ = con.execute(self.__make_select_statement(), (self.account,)).fetchone()[0]
        con.close()

        try:
            result = self.__verify_hash(password, hash_)
        except argon2.exceptions.VerifyMismatchError:
            return False
        else:
            return result
                
    def delete_account(self) -> None:
        con = self.__make_con()
        
        with con:
            con.execute("DELETE FROM passwords WHERE account_name = ?", (self.account,))
            con.execute("DELETE FROM user_login WHERE account_name = ?", (self.account,))
        
        con.close()


class ProfileFactory:
    def __make_insert_statement(self) -> str:
        return "INSERT INTO user_login \
            (account_name, password_hash, salt) \
                VALUES (?, ?, ?);"
    
    def __make_select_statement(self) -> str:
        return "SELECT password_hash, salt FROM user_login WHERE account_name = ?;"

    def __get_hasher(self) -> argon2.PasswordHasher:
        return argon2.PasswordHasher()

    def __hash_password(self, password: str) -> str:
        ph = self.__get_hasher()
        password_hash = ph.hash(password)
        del password

        return password_hash
    
    def __verify_hash(self, raw: str, hashed: str) -> bool:
        ph = self.__get_hasher()
        
        return ph.verify(hashed, raw)

    def __make_salt(self, length: int = 16) -> str:
        return ''.join([choice(string.ascii_letters + string.digits) for _ in range(length)])

    def register_profile(self, username, password) -> Profile:
        con = sqlite3.connect("passwords.db")
        salt = self.__make_salt()

        try:
            # insert to database
            with con:
                con.execute(
                    self.__make_insert_statement(), 
                    (
                        username,
                        self.__hash_password(password),
                        salt
                    )
                )

        except sqlite3.IntegrityError:
            # if username already exists
            con.close()
            raise UsernameAlreadyExists("Username already exists!")
        else:
            # successful. close and return
            con.close()

            return Profile(username, password, salt)
        
    def login_profile(self, username, password) -> Profile:
        # select from database
        con = sqlite3.connect("passwords.db")
        query = con.execute(self.__make_select_statement(), (username,)).fetchone()
        con.close()

        # check username exists
        if query is None:
            raise UsernameDoesNotExist("Account does not exist")
        
        hash_, salt = query

        # verify password
        try:
            self.__verify_hash(password, hash_)
        except argon2.exceptions.VerifyMismatchError:
            raise WrongPassword("Password is incorrect")
        else:
            return Profile(username, password, salt)
        

class EntryAlreadyExist(Exception):
    pass

class UsernameAlreadyExists(Exception):
    pass

class UsernameDoesNotExist(Exception):
    pass

class WrongPassword(Exception):
    pass
