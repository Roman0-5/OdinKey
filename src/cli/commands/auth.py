import click  
import getpass
import sqlite3
from src.core.session import Session
from src.database.connection import DatabaseConnection
from src.database.repository import MasterAccountRepository
from src.services.master_account_service import MasterAccountService

#Abhängigkeiten
db_conn = DatabaseConnection()
repo = MasterAccountRepository(db_conn)
service = MasterAccountService(repo)

# Create a global session object
session = Session()


@click.command()
def register():
    #Neuen Master-Account anlegen
    click.echo("OdinKey Registrierung")

    # DB Tabellen erstellen, falls erster Start
    db_conn.create_tables()

    username = click.prompt("Wähle einen Benutzernamen")
    password = getpass.getpass("Wähle ein starkes Master-Passwort: ")
    password_confirm = getpass.getpass("Passwort wiederholen: ")

    if password != password_confirm:
        click.echo("Fehler: Passwörter stimmen nicht überein.")
        return

    try:
        service.register_account(username, password)
        click.echo(f"Erfolg! Account '{username}' wurde erstellt. Du kannst dich jetzt einloggen.")
    except ValueError as e:
        click.echo(f"Fehler: {str(e)}")
    except Exception as e:
        click.echo(f"Unerwarteter Fehler: {e}")

# Simple login function for user login
@click.command()
def login():
        #In OdinKey einloggen.
        # Prüfen ob ein Account da ist.
        # Wenn die Tabelle fehlt (OperationalError), werten wir das wie "Kein Account".
    try:
        if not repo.account_exists():
            click.echo("Kein Account gefunden. Bitte zuerst registrieren:")
            click.echo("  python cli_main.py register")
            return

    except sqlite3.OperationalError:
            # Fehler kommt, wenn die Tabelle noch gar nicht existiert
        click.echo("Datenbank ist noch leer. Bitte zuerst registrieren:")
        click.echo("  python cli_main.py register")
        return

    # Ask the user to enter username
    username = click.prompt("Username")  # Oder input(), click.prompt ist aber schöner
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

    else:
        click.echo("Login fehlgeschlagen. Falscher Username oder Passwort.")
        session.end()

@click.command()
def logout():
    #Session beenden
    if session.is_active():
        session.end()
        click.echo("Erfolgreich ausgeloggt.")
    else:
        click.echo("Du bist gar nicht eingeloggt.")