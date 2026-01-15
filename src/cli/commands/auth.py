import click
import getpass
import sqlite3
import sys
from colorama import Fore, Style

from src.core.master_account import MasterAccount
from src.core.session import session
from src.database.connection import db as db_conn
from src.database.repository import MasterAccountRepository
from src.services.master_account_service import MasterAccountService

#Abhängigkeiten
repo = MasterAccountRepository(db_conn)
service = MasterAccountService(repo)



def register():
    #Neuen Master-Account anlegen
    MasterAccountRepository(db_conn)
    MasterAccountService(repo)
    # DB Tabellen erstellen, falls erster Start
    db_conn.create_tables()

    username = input("Wähle einen Benutzernamen: ")
    if sys.stdin.isatty():
        password = getpass.getpass("Wähle ein starkes Master-Passwort: ")
        password_confirm = getpass.getpass("Passwort wiederholen: ")
    else:
        print("Wähle ein starkes Master-Passwort: ", end="", flush=True)
        password = getpass.getpass("")
        print("Passwort wiederholen: ", end="", flush=True)
        password_confirm = getpass.getpass("")

    if password != password_confirm:
        print("Fehler: Passwörter stimmen nicht überein.")
        return False
    try:
        service.register_account(username, password)
        click.echo(f"Erfolg! Account '{username}' wurde erstellt. Du kannst dich jetzt einloggen.")
    except ValueError as e:
        click.echo(f"Fehler: {str(e)}")
        return False
    except Exception as e:
        click.echo(f"Unerwarteter Fehler: {e}")
        return False
# Simple login function for user login
def login():
        #In OdinKey einloggen.
        # Prüfen ob ein Account da ist.
        # Wenn die Tabelle fehlt (OperationalError), werten wir das wie "Kein Account".
    try:
        if not repo.account_exists():
            print("Kein Account gefunden. Bitte zuerst registrieren mit " + Fore.YELLOW + "register")
            return False

    except sqlite3.OperationalError:
            # Fehler kommt, wenn die Tabelle noch gar nicht existiert
        click.echo("Datenbank ist noch leer. Bitte zuerst registrieren:")
        click.echo("  python cli_main.py register")
        return False

    # Ask the user to enter username
    username = input("Username: ")  # Oder input(), click.prompt ist aber schöner
    # Ask the user to enter password (input is hidden)
    password = getpass.getpass("Password: ")

    #Login-Versuch über den Service
    result = service.login(username, password)

    if result:
        account, master_key = result
        # Session starten
        session.start(account, master_key)
        click.echo(f"Login erfolgreich! Willkommen zurück, {account.username}.")
        click.echo("Session ist aktiv. (Timeout: 10 Minuten)")
        return True
    else:
        click.echo("Login fehlgeschlagen. Falscher Username oder Passwort.")
        session.end()
        return False

def logout():
    #Session beenden
    if session.is_active():
        session.end()
        click.echo("Erfolgreich ausgeloggt.")
        return True
    else:
        click.echo("Du bist gar nicht eingeloggt.")
        return False