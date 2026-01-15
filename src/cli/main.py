import click
import sys
import getpass
import sqlite3

from src.cli.commands.generator import generate

# Falls colorama fehlt: pip install colorama
try:
    from colorama import init, Fore, Style

    init()
except ImportError:
    # Fallback
    class Fore:
        GREEN = "";
        RED = "";
        YELLOW = "";
        CYAN = "";
        MAGENTA = ""


    class Style:
        RESET_ALL = ""

from src.database.connection import db as db_conn
from src.database.repository import MasterAccountRepository
from src.services.master_account_service import MasterAccountService
from src.core.session import session
from src.cli.commands import auth
from src.services.password_generator_service import PasswordGeneratorService

# IMPORTS FÜR PASSWORT-MANAGER
from src.core.password_profile import PasswordProfile
from src.database.password_profile_repository import PasswordProfileRepository

# <--- NEU: Backend-Service Import ---
from src.services.password_profile_service import PasswordProfileService
# ------------------------------------

from src.utils.clipboard import copy_with_timeout

# --- SETUP ---
repo = MasterAccountRepository(db_conn)
service = MasterAccountService(repo)
auto_logged_out = False # session management flag - autologout

def print_banner():
    print(Fore.YELLOW + r"""
   ____  _     _       _  __
  / __ \| |   (_)     | |/ /
 | |  | | |__  _ _ __ | ' / ___ _   _ 
 | |  | | '_ \| | '_ \|  < / _ \ | | |
 | |__| | | | | | | | | . \  __/ |_| |
  \____/|_| |_|_|_| |_|_|\_\___|\__, |
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
    print(f" {Fore.CYAN}list{Style.RESET_ALL}     - Alle Passwörter anzeigen")
    print(f" {Fore.CYAN}add{Style.RESET_ALL}      - Neues Passwort speichern")
    print(f" {Fore.CYAN}delete{Style.RESET_ALL}   - Eintrag löschen")
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


def handle_generate():
    """Generiert ein Passwort mit konfigurierbaren Optionen."""
    print("\n--- Passwort Generator ---")
    try:
        length_str = input("Länge (Enter für 12): ")
        length = int(length_str) if length_str else 12
    except ValueError:
        length = 12

    # Optionen abfragen
    use_upper = ask_bool("Großbuchstaben verwenden?", default=True)
    use_lower = ask_bool("Kleinbuchstaben verwenden?", default=True)
    use_digits = ask_bool("Ziffern verwenden?", default=True)
    use_special = ask_bool("Sonderzeichen verwenden?", default=True)
    use_copy = ask_bool("Kopieren?", default=False)
    generate(
        length=length,
        uppercase=use_upper,
        lowercase=use_lower,
        digits=use_digits,
        special=use_special,
        copy=use_copy
    )

def interactive_loop():
    global auto_logged_out
    print_banner()
    print_menu_logged_out()

    while True:
        # Prompt Design
        if auto_logged_out:
            print(Fore.YELLOW + " Session Expired! Du wurdest automatisch ausgeloggt." + Style.RESET_ALL)
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

            parts = user_input.split()
            command = parts[0].lower()



            if command in ["exit", "quit", "q"]:
                print("Auf Wiedersehen!")
                break

            elif command == "help":
                if session.is_active():
                    print_menu_logged_in(session.account.username)
                else:
                    print_menu_logged_out()

            elif command == "login":
                if session.is_active():
                    print("Du bist bereits eingeloggt.")
                else:
                    if auth.login():
                        print_menu_logged_in(session.account.username)

            elif command == "register":
                if session.is_active():
                    print("Bitte erst ausloggen.")
                else:
                    auth.register()
            elif command == "logout":
                if auth.logout():
                    print_menu_logged_out()
                else:
                    print("Du bist nicht eingeloggt.")

            elif command == "generate":
                handle_generate()

            elif command == "add":
                if session.is_active():
                    handle_add()
                else:
                    print(Fore.RED + "Zugriff verweigert. Bitte einloggen." + Style.RESET_ALL)

            elif command == "list":
                if session.is_active():
                    handle_list(interactive=True)
                else:
                    print(Fore.RED + "Zugriff verweigert. Bitte einloggen." + Style.RESET_ALL)

            elif command == "delete":
                if session.is_active():
                    handle_delete()
                else:
                    print(Fore.RED + "Zugriff verweigert. Bitte einloggen." + Style.RESET_ALL)

            elif command == "search":
                if session.is_active():
                    handle_search()
                else:
                    print(Fore.RED + "Zugriff verweigert." + Style.RESET_ALL)

            else:
                print(f"Unbekannter Befehl. Tippe 'help' für eine Übersicht.")

        except KeyboardInterrupt:
            print("\nBeenden mit 'exit'")
            break
        except Exception as e:
            print(Fore.RED + f"Kritischer Fehler: {e}" + Style.RESET_ALL)


@click.command()
def main():
    interactive_loop()


if __name__ == '__main__':
    main()