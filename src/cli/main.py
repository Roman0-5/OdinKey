import click
import traceback
from colorama import init, Fore, Style

from src.cli.commands.generator import generate_random

init()


# Database
from src.database.connection import db as db_conn
from src.database.repository import MasterAccountRepository
# MasterAccount
from src.services.master_account_service import MasterAccountService
# Session Management
from src.core.session import session
# commands
from src.cli.commands import auth
from src.cli.commands import generator
from src.cli.commands import profile
# Setup
repo = MasterAccountRepository(db_conn)
service = MasterAccountService(repo)
auto_logged_out = False # session management flag - autologout

def print_banner():
    print(Fore.YELLOW + r"""
   ____      _         _  __
  / __ \    | (_)     | |/ /
 | |  | | __| |_ _ __ | ' / ___ _   _
 | |  | |/ _` | | '_ \|  < / _ \ | | |
 | |__| | (_| | | | | | . \  __/ |_| |
  \____/ \__,_|_|_| |_|_|\_\___|\__, |
                                 __/ |
                                |___/
    """ + Style.RESET_ALL)


def print_menu_logged_out():
    """Zeigt Optionen für Gäste"""
    print(f"\n{Fore.MAGENTA}--- Hauptmenü (Gesperrt) ---{Style.RESET_ALL}")
    print(f" {Fore.CYAN}login{Style.RESET_ALL}    - Anmelden")
    print(f" {Fore.CYAN}register{Style.RESET_ALL} - Account erstellen")
    print(f" {Fore.CYAN}generate{Style.RESET_ALL} - Passwort generieren (Quick)")
    print(f" {Fore.CYAN}exit{Style.RESET_ALL}     - Beenden")
    print("-" * 30)


def print_menu_logged_in(username):
    """Zeigt Optionen für eingeloggte User"""
    print(f"\n{Fore.GREEN}--- Tresor von {username} ---{Style.RESET_ALL}")
    print(f" {Fore.CYAN}help{Style.RESET_ALL}     - Zeigt Alle Befehle")
    print(f" {Fore.CYAN}list{Style.RESET_ALL}     - Alle Passwörter anzeigen")
    print(f" {Fore.CYAN}add{Style.RESET_ALL}      - Neues Passwort speichern")
    print(f" {Fore.CYAN}manage{Style.RESET_ALL}   - Profile verwalten (Edit/Delete)") # NEU
    print(f" {Fore.CYAN}generate{Style.RESET_ALL} - Passwort generieren")
    print(f" {Fore.CYAN}search{Style.RESET_ALL}   - Nach Einträgen suchen")
    print(f" {Fore.CYAN}logout{Style.RESET_ALL}   - Tresor schließen")
    print("-" * 30)

def on_session_expire():
    global auto_logged_out
    auto_logged_out = True
session.set_expire_callback(on_session_expire)

def ask_bool(prompt, default=True):
    """Hilfsfunktion für Ja/Nein Abfragen."""
    suffix = " [Y/n]" if default else " [y/N]"
    val = input(prompt + suffix + ": ").strip().lower()
    if not val:
        return default
    return val in ["y", "yes", "j", "ja"]

# Command Handlers
def cmd_exit():
    print("Auf Wiedersehen!")
    return True

def cmd_help():
    if session.is_active():
        print_menu_logged_in(session.account.username)
    else:
        print_menu_logged_out()

def cmd_login():
    if session.is_active():
        print("Bereits eingeloggt")
    else:
        if auth.login():
            print_menu_logged_in(session.account.username)

# command registry
COMMANDS = {
    'help': cmd_help,
    # auth
    'login': cmd_login,
    'register': auth.register,
    # generator
    'generate': generator.generate,
    'gen': generator.generate,
    # profile
    'manage': profile.manage_menu,
    'add': profile.add,
    'list': profile.list_passwords,
    'search': profile.search,
    # Close Program
    'exit': cmd_exit,
    'quit': cmd_exit,
    'q': cmd_exit
}
def interactive_loop():
    global auto_logged_out
    print_banner()
    print_menu_logged_out()

    while True:
        if auto_logged_out:
            print("\n" + Fore.YELLOW + "Session expired! Du wurdest automatisch ausgeloggt." + Style.RESET_ALL)
            print_menu_logged_out()
            auto_logged_out = False

        if session.is_active():
            session.touch()
            prompt = f"{Fore.GREEN}OdinKey ({session.account.username}){Style.RESET_ALL} > "
        else:
            prompt = f"{Fore.RED}OdinKey (locked | tippe 'help'){Style.RESET_ALL} > "

        try:
            user_input = input(prompt).strip()

            if not user_input:
                continue

            command = user_input.split()[0].lower()

            if command in COMMANDS:
                result = COMMANDS[command]()
                if result is True:
                    break
            else:
                print(f"Unbekannter Befehl: {command}. Tippe 'help'.")

        except KeyboardInterrupt:
            print("\nBeenden mit 'exit'")
            break
        except Exception as e:
            print(Fore.RED + f"Kritischer Fehler: {e}" + Style.RESET_ALL)
            traceback.print_exc()

@click.command()
def main():
    interactive_loop()


if __name__ == '__main__':
    main()