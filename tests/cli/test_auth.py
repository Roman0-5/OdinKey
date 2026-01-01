import pytest
import sys
import os
import builtins
import getpass

# Add the project root to sys.path so imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.cli.commands.auth import login, session
from src.core.master_account import MasterAccount

# This fixture resets the session before every test
@pytest.fixture(autouse=True)
def reset_session():
    session.end()

# This fixture lets you set username and password for tests
# It replaces input() and getpass.getpass() only for the test
@pytest.fixture
def user0():
    # Save the original input and getpass.getpass functions
    orig_input = builtins.input
    orig_getpass = getpass.getpass

    class User0:
        def set(self, username, password):
            self.username = username
            self.password = password
        def input(self, prompt):
            return self.username
        def getpass(self, prompt):
            return self.password

    u = User0()
    # Replace input and getpass.getpass with our test versions
    builtins.input = u.input
    getpass.getpass = u.getpass

    yield u  # Give the test access to user0

    # Restore the original functions after the test
    builtins.input = orig_input
    getpass.getpass = orig_getpass

def test_login_success(user0, capsys):
    """
    This test checks that login works with correct username and password.
    """
    user0.set('test', '1234')
    login.callback() # Call the command function directly
    out = capsys.readouterr().out
    assert "Login successful" in out
    assert session.is_active() is True
    assert session.account.username == 'test'

def test_login_wrong_password(user0, capsys):
    """
    This test checks that login fails with wrong password.
    """
    user0.set('test', 'wrong')
    login.callback() 
    out = capsys.readouterr().out
    assert "Login failed" in out
    assert session.is_active() is False

def test_login_wrong_username(user0, capsys):
    """
    This test checks that login fails with wrong username.
    """
    user0.set('wronguser', '1234')
    login.callback() 
    out = capsys.readouterr().out
    assert "Login failed" in out
    assert session.is_active() is False

def test_session_end():
    """
    This test checks that end() makes session not active.
    """
    acc = MasterAccount(id=1, username="test", password="pw")
    session.start(account=acc, master_key=b"secret")
    session.end()
    assert session.is_active() is False