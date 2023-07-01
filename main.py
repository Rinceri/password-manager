import argon2
from getpass import getpass
import sqlite3
from os import urandom
import pyperclip
from cryptography.fernet import Fernet
import base64
from secrets import choice
import string

def new_profile():
    """
    Creates a new profile. Asks and stores username, master password and salt for PBKDF
    """
    def create_profile():
        while True:
            account_name = input('Enter account name: ')
            password = getpass('Enter password: ')
            password_again = getpass('Enter password again: ')

            if password != password_again:
                print("Wrong password entered. Rerunning setup...")
            else:
                ph = argon2.PasswordHasher()
                password_hash = ph.hash(password)
                salt = ''.join([choice(string.ascii_letters + string.digits) for i in range(16)])
                del password, password_again

                return (account_name, password_hash, salt)
    
    account_name, password_hash, salt = create_profile()

    # store profile
    con = sqlite3.connect('passwords.db')

    with con:
        # try saving the profile, if account_name already exists, raises an error and re-runs the create_profile func
        # tries inserting again
        while True:
            try:
                con.execute(
                    """
                    INSERT INTO user_login (account_name, password_hash, salt)
                    VALUES (?, ?, ?);
                    """,
                    (account_name, password_hash, salt))
                break

            except:
                print("An account with this name already exists!")
                account_name, password_hash, salt = create_profile()
    con.close()

    print("Profile has been created")


def login():
    """
    Logs in the user. Returns plaintext password and salt if user is successful in logging in, else returns False boolean
    """
    account_name = input("Enter account name: ")
    
    con = sqlite3.connect('passwords.db')
    query = con.execute("SELECT password_hash, salt FROM user_login WHERE account_name = ?;", (account_name,)).fetchone()
    con.close()

    if query is None:
        print("Account with this name does not exist.")
        return False
    
    password_hash, salt = query

    password = getpass("Enter master password: ")

    ph = argon2.PasswordHasher()
    
    try:
        ph.verify(password_hash, password)
        return account_name, password, salt

    except:
        print("Failed to verify entered password. Try again.")
        return False


def menu(account_name: str, plaintext_password: str, salt: str):
    """
    Main menu upon logging in
    """

    while True:
        print(
            """
            Welcome! What do you wish to do?
            > (R)etrieve login details
            > (S)ave new website login details
            > (D)elete website login details
            > Delete profile (type: delete profile)
            > (L)ogout
            """)

        inp = input(">> ")

        if inp.lower()[0] == 'r':
            retrieve_profile_menu(account_name, plaintext_password, salt)

        elif inp.lower()[0] == 's':
            save_login_menu(account_name, plaintext_password, salt)
        
        elif inp.lower() == 'delete profile':
            status = delete_profile_menu(account_name)
            if status:
                exit()

        elif inp.lower()[0] == 'd':
            delete_login_menu(account_name)

        elif inp.upper()[0] == 'L':
            exit()
        
def retrieve_profile_menu(account_name: str, plaintext_password: str, salt: str):
    """
    Function run when user presses "R"
    """
    con = sqlite3.connect('passwords.db')

    # create prompt for user to select from
    records = con.execute("SELECT * FROM passwords WHERE account_name = ?", (account_name,)).fetchall()
    con.close()

    prompt = ""
    counter = 0

    for record in records:
        counter += 1
        prompt += "{0}. Website/app: {1} // Username: {2}\n".format(counter, record[2], record[1])
    prompt += "\nPress 'E' to exit"

    print("Choose which password to see:\n", prompt)

    # input
    while True:
        inp = input(">> ")

        if inp.lower() == 'e':
            print("Exiting")
            return

        try:
            inp = int(inp)

            if inp in range(1, counter+1):
                break
            raise
        except:
            print("Enter a number that is within the range")
    
    # hash plaintext master password, with salt specific to the user, and use that as key to decrypt
    record = records[inp - 1]
    hashed_password = argon2.low_level.hash_secret(
        secret = plaintext_password.encode(), 
        salt = salt.encode(), 
        time_cost = 3,
        memory_cost = 65536, 
        parallelism = 4, hash_len = 30, 
        type = argon2.Type.ID)

    key = Fernet(base64.urlsafe_b64encode(hashed_password[-32:]))
    
    plaintext_website_password = key.decrypt(record[3]).decode()

    pyperclip.copy(plaintext_website_password)
    
    print(">>>>>>>>>  Website password copied to clipboard!")

def save_login_menu(account_name: str, plaintext_password: str, salt: str):
    """
    Function run when user presses "S"
    """
    def cancel_wizard(inp: str):
        if inp.lower() == 'c':
            print("Login wizard cancelled.")
            return True
        return False

    # Enter website name and username
    print("New login wizard\nPress (C) to cancel anytime.")
    print("Enter website name:")
    website = input(">> ")
    if cancel_wizard(website):
        return

    print("Enter username for the site:")
    username = input(">> ")
    if cancel_wizard(username):
        return

    # Create a random password or or enter your own
    while True:
        print("Create random password (R) OR enter your own (O)?")
        pass_prompt_answer = input(">> ")
        
        if cancel_wizard(pass_prompt_answer):
            return
        elif pass_prompt_answer.lower()[0] == 'r':
            login_password = ''.join(choice(string.printable) for i in range(30))
            break
        elif pass_prompt_answer.lower()[0] == 'o':
            login_password = getpass("Enter your password:")
            break
        else:
            print("Invalid character entered. Try again or cancel with (C)")

    # Encrypt password using key
    hashed_password = argon2.low_level.hash_secret(
        secret = plaintext_password.encode(), 
        salt = salt.encode(), 
        time_cost = 3,
        memory_cost = 65536, 
        parallelism = 4, hash_len = 30, 
        type = argon2.Type.ID)

    key = Fernet(base64.urlsafe_b64encode(hashed_password[-32:]))

    encrypted_login_password = key.encrypt(login_password.encode())

    con = sqlite3.connect('passwords.db')

    with con:
        try:
            con.execute("""
            INSERT INTO passwords (account_name, username, website, encrypted_password) 
            VALUES (?, ?, ?, ?)
            """, (account_name, username, website, encrypted_login_password.decode())
            )
        except:
            print("An error occured.")
        else:
            print("Login details saved!")

    con.close()

def delete_login_menu(account_name: str):
    """
    Function run when user presses "D"
    """
    con = sqlite3.connect('passwords.db')

    # create prompt for user to select from
    records = con.execute("SELECT * FROM passwords WHERE account_name = ?", (account_name,)).fetchall()
    
    prompt = ""
    counter = 0

    for record in records:
        counter += 1
        prompt += "{0}. Website/app: {1} // Username: {2}\n".format(counter, record[2], record[1])
    prompt += "\nPress 'E' to exit"

    print("Choose which login details to delete:\n", prompt)

    # input
    while True:
        inp = input(">> ")
        
        if inp.lower() == 'e':
            print('Exiting')
            con.close()
            return

        try:
            inp = int(inp)

            if inp in range(1, counter+1):
                break
            raise
        except:
            print("Enter a number that is within the range")

    record = records[inp - 1]
    print("Are you sure you want to delete these login details? Type the username if you wish to delete it: ")
    entered_username = input(">> ")

    if record[1] == entered_username:
        with con:
            con.execute("DELETE FROM passwords WHERE account_name = ? AND username = ? AND website = ?", (account_name, record[1], record[2]))

        print("Login details for this username and website sucessfully deleted.")
    else:
        print("Username does not match with what was entered. Process cancelled.")
    
    con.close()

def delete_profile_menu(account_name) -> bool:
    """
    Function run when user types "delete profile"
    """
    password = getpass("Enter password for this account:")
    # return variable status returns whether the account was deleted or not
    status = False
    con = sqlite3.connect('passwords.db')
    password_hash = con.execute("SELECT password_hash FROM user_login WHERE account_name = ?", (account_name,)).fetchone()[0]

    ph = argon2.PasswordHasher()

    try:
        ph.verify(password_hash, password)
    except:
        print("Incorrect master password entered.")
    else:
        print("Are you sure you want to delete the account? Type 'DELETE ACCOUNT' to confirm.")
        inp = input(">> ")

        if inp.upper() == 'DELETE ACCOUNT':
            print("Deleting account...")

            with con:
                con.execute("DELETE FROM passwords WHERE account_name = ?", (account_name,))
                con.execute("DELETE FROM user_login WHERE account_name = ?", (account_name,))
            
            print("Account deleted.")
            status = True
        else:
            print("Cancelled process.")

    con.close()
    return status

if __name__ == '__main__':
    while True:   
        print("""
Create (N)ew profile,
(L)og in to existing profile
            """)
        
        inp = input(">> ")

        if inp.lower()[0] == "n":
            new_profile()
        
        elif inp.upper()[0] == "L":
            out = login()

            if type(out) == tuple:
                account_name, plaintext_password, salt = out
            
            else:
                continue
                
            menu(account_name, plaintext_password, salt)

        
        else:
            print("Option does not exist.")