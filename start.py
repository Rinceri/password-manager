from getpass import getpass
import argon2
import sqlite3
from secrets import choice
import string

# Create profile
while True:
    account_name = input('Enter account name: ')
    password = getpass('Enter password: ')
    password_again = getpass('Enter password again: ')

    if password != password_again:
        print("Wrong password entered. Rerunning setup...")
    else:
        break


# Hash password
ph = argon2.PasswordHasher()
password_hash = ph.hash(password)
del password, password_again

# Generate random salt (needed for PBKDF)
salt = ''.join([choice(string.ascii_letters + string.digits) for i in range(16)])

# Create login table; Store login info; Create password table
con = sqlite3.connect('passwords.db')

with con:
    con.execute("""CREATE TABLE user_login (
        account_name TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        salt TEXT
        );""")
    
    con.execute("""
        INSERT INTO user_login (account_name, password_hash, salt)
        VALUES (?, ?, ?);
        """,
        (account_name, password_hash, salt))
    
    con.execute("""
        CREATE TABLE passwords (
            account_name TEXT,
            username TEXT,
            website TEXT,
            encrypted_password TEXT,

            PRIMARY KEY (account_name, username, website)
        );""")

con.close()


print("Setup is complete!")