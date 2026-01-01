import click  
import getpass  
from src.core.session import Session  
from src.core.master_account import MasterAccount  

# Create a global session object
session = Session()

# Simple login function for user login
@click.command()
def login():
    # Ask the user to enter username
    username = input("Username: ")
    # Ask the user to enter password (input is hidden)
    password = getpass.getpass("Password: ")

    # FOR EXAMPLE ONLY: check username and password directly
    # In the future, we will check user in the database
    if username == 'test' and password == '1234':
        # If correct, create a MasterAccount object
        account = MasterAccount(id=1, username=username, password='hashed_pw')
        # Use a simple master_key for this example
        master_key = b"secret"
        # Start the session with this account and key
        session.start(account, master_key)
        # Print a success message for the user
        print("Login successful. Session started for", username)
    else:
        # If username or password is wrong, do not start session
        print("Login failed. Wrong username or password.")
        # Make sure session is not active
        session.end()