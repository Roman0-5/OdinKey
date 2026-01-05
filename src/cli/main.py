import click
import sys
import getpass
import sqlite3

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

from src.database.connection import DatabaseConnection
from src.database.repository import MasterAccountRepository
from src.services.master_account_service import MasterAccountService
from src.core.session import Session
from src.services.password_generator_service import PasswordGeneratorService

# IMPORTS FÜR PASSWORT-MANAGER
from src.core.password_profile import PasswordProfile
from src.database.password_profile_repository import PasswordProfileRepository

# <--- NEU: Unser Shared Utility Modul
from src.utils.clipboard import copy_with_timeout

# --- SETUP ---
db_conn = DatabaseConnection()
repo = MasterAccountRepository(db_conn)
service = MasterAccountService(repo)
session = Session()


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
    print(f" {Fore.CYAN}search{Style.RESET_ALL} - Nach Einträgen suchen")
    print(f" {Fore.CYAN}logout{Style.RESET_ALL}   - Tresor schließen")
    print("-" * 30)


def handle_login():
    if not repo.account_exists():
        print(Fore.RED + "Kein Account gefunden. Bitte nutze zuerst 'register'." + Style.RESET_ALL)
        return False

    username = input("Username: ")

    print("Password: ", end="", flush=True)
    password = getpass.getpass("")

    result = service.login(username, password)
    if result:
        account, master_key = result
        session.start(account, master_key)
        print(Fore.GREEN + f"Login erfolgreich! Hallo {account.username}." + Style.RESET_ALL)
        return True
    else:
        print(Fore.RED + "Falsches Passwort oder Username." + Style.RESET_ALL)
        return False


def handle_register():
    print("--- Neuer Master Account ---")
    db_conn.create_tables()

    username = input("Wähle Username: ")

    print("Master-Passwort: ", end="", flush=True)
    pw1 = getpass.getpass("")

    print("Wiederholen:     ", end="", flush=True)
    pw2 = getpass.getpass("")

    if pw1 != pw2:
        print(Fore.RED + "Passwörter stimmen nicht überein." + Style.RESET_ALL)
        return

    try:
        service.register_account(username, pw1)
        print(Fore.GREEN + "Account erstellt! Bitte jetzt einloggen." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Fehler: {e}" + Style.RESET_ALL)


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

    gen_service = PasswordGeneratorService()
    result = gen_service.generate_password(
        length=length,
        use_uppercase=use_upper,
        use_lowercase=use_lower,
        use_digits=use_digits,
        use_special=use_special
    )

    if result['success']:
        print(f"Generiert: {Fore.CYAN}{result['password']}{Style.RESET_ALL}")
    else:
        # Fehlermeldung (z.B. wenn gar keine Option gewählt wurde)
        print(Fore.RED + f"Fehler: {result['error']}" + Style.RESET_ALL)


def handle_add():
    """Fügt ein neues Passwort hinzu und verschlüsselt es."""
    if not session.is_active():
        print(Fore.RED + "Session abgelaufen." + Style.RESET_ALL)
        return

    print("\n--- Neues Passwort anlegen ---")
    service_name = input("Service (z.B. Google): ")
    if not service_name:
        print(Fore.RED + "Abbruch: Service Name ist Pflicht." + Style.RESET_ALL)
        return

    username = input("Username/Email: ")
    if not username:
        print(Fore.RED + "Abbruch: Username ist Pflicht." + Style.RESET_ALL)
        return

    url = input("URL (optional): ")

    print("Passwort: ", end="", flush=True)
    password = getpass.getpass("")
    if not password:
        print(Fore.RED + "Abbruch: Passwort darf nicht leer sein." + Style.RESET_ALL)
        return

    try:
        # Profil-Objekt erstellen
        profile = PasswordProfile(
            user_id=session.account.id,
            service_name=service_name,
            url=url,
            username=username,
            password=password
        )

        # Repository initialisieren (braucht Master Key zum Verschlüsseln)
        repo_profile = PasswordProfileRepository(db_conn, session.get_master_key())
        repo_profile.create_profile(profile)

        print(Fore.GREEN + f"Eintrag für '{service_name}' erfolgreich verschlüsselt gespeichert!" + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + f"Fehler beim Speichern: {e}" + Style.RESET_ALL)


def handle_list(interactive=True):
    """Listet alle Passwörter auf. Wenn interactive=True, kann man entschlüsseln."""
    if not session.is_active():
        return

    user_id = session.account.id

    conn = db_conn.connect()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, service_name, username, url FROM password_profiles WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()

        if not rows:
            print(Fore.YELLOW + "Keine Passwörter gefunden." + Style.RESET_ALL)
            conn.close()
            return

        # Tabelle ausgeben
        print(f"\n{Fore.CYAN}{'ID':<5} {'Service':<20} {'Username':<25} {'URL'}{Style.RESET_ALL}")
        print("-" * 70)

        for row in rows:
            s_name = row['service_name'] if row['service_name'] else ""
            u_name = row['username'] if row['username'] else ""
            url = row['url'] if row['url'] else ""
            print(f"{row['id']:<5} {s_name:<20} {u_name:<25} {url}")

        print("-" * 70)

        # Nur fragen, wenn interactive True ist
        if interactive:
            choice = input("\nID eingeben zum Entschlüsseln (oder Enter für zurück): ").strip()
            if choice and choice.isdigit():
                reveal_password(int(choice))

    except Exception as e:
        print(Fore.RED + f"Fehler beim Laden: {e}" + Style.RESET_ALL)
    finally:
        conn.close()


def reveal_password(profile_id):
    """Entschlüsselt Passwort, kopiert es und löscht es nach 60 Sek."""
    try:
        repo_profile = PasswordProfileRepository(db_conn, session.get_master_key())
        profile = repo_profile.get_profile_by_id(profile_id)

        if profile and profile.user_id == session.account.id:
            print(f"Eintrag gefunden: {Fore.CYAN}{profile.service_name} ({profile.username}){Style.RESET_ALL}")

            # <--- HIER: Aufruf der zentralen Utility-Funktion
            if copy_with_timeout(profile.password, timeout=60):
                print(f"{Fore.GREEN}✔ Passwort wurde in die Zwischenablage kopiert!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}(Sicherheits-Feature: Zwischenablage leert sich in 60 Sek.){Style.RESET_ALL}")

            if ask_bool("Soll das Passwort zusätzlich angezeigt werden?", default=False):
                print(f"Passwort: {Fore.RED}{profile.password}{Style.RESET_ALL}")

            input("Drücke Enter um fortzufahren...")
        else:
            print(Fore.RED + "Eintrag nicht gefunden oder kein Zugriff." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + f"Fehler beim Entschlüsseln: {e}" + Style.RESET_ALL)


def handle_delete():
    """Löscht einen Eintrag nach erneuter Passwort-Bestätigung."""
    if not session.is_active():
        return

    # Aufruf mit interactive=False, damit keine Frage kommt
    handle_list(interactive=False)

    try:
        id_str = input("\nWelche ID soll gelöscht werden? (Enter für Abbruch): ").strip()
        if not id_str:
            return

        profile_id = int(id_str)

        print(f"{Fore.YELLOW}ACHTUNG: Löschen erfordert Bestätigung.{Style.RESET_ALL}")
        print("Master-Passwort: ", end="", flush=True)
        conf_pw = getpass.getpass("")

        # Prüfung über Login-Funktion
        if not service.login(session.account.username, conf_pw):
            print(Fore.RED + "Falsches Passwort. Löschen abgebrochen." + Style.RESET_ALL)
            return

        repo_profile = PasswordProfileRepository(db_conn, session.get_master_key())

        profile = repo_profile.get_profile_by_id(profile_id)
        if profile and profile.user_id == session.account.id:
            repo_profile.delete_profile(profile_id)
            print(Fore.GREEN + f"Eintrag ID {profile_id} wurde unwiderruflich gelöscht." + Style.RESET_ALL)
        else:
            print(Fore.RED + "Eintrag nicht gefunden." + Style.RESET_ALL)

    except ValueError:
        print(Fore.RED + "Ungültige ID." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Fehler: {e}" + Style.RESET_ALL)


def handle_search():
    """Sucht nach Einträgen über das Repository."""
    if not session.is_active():
        return

    query = input("Suchbegriff: ").strip()
    if not query:
        return

    try:
        # Repository initialisieren
        repo_profile = PasswordProfileRepository(db_conn, session.get_master_key())
        profiles = repo_profile.search_profiles(session.account.id, query)

        if not profiles:
            print(Fore.YELLOW + "Keine Treffer." + Style.RESET_ALL)
            return

        print(f"\n{Fore.CYAN}{'ID':<5} {'Service':<20} {'Username':<25} {'URL'}{Style.RESET_ALL}")
        print("-" * 70)

        for p in profiles:
            s_name = p.service_name if p.service_name else ""
            u_name = p.username if p.username else ""
            url = p.url if p.url else ""
            print(f"{p.id:<5} {s_name:<20} {u_name:<25} {url}")

        print("-" * 70)

        # Direkt anbieten zu entschlüsseln
        choice = input("\nID zum Entschlüsseln (oder Enter für zurück): ").strip()
        if choice and choice.isdigit():
            reveal_password(int(choice))

    except Exception as e:
        print(Fore.RED + f"Such-Fehler: {e}" + Style.RESET_ALL)


def interactive_loop():
    print_banner()

    # Initiale Menü-Anzeige
    print_menu_logged_out()

    while True:
        # Prompt Design
        if session.is_active():
            prompt = f"{Fore.GREEN}OdinKey ({session.account.username}){Style.RESET_ALL} > "
        else:
            prompt = f"{Fore.RED}OdinKey (locked | tippe 'help'){Style.RESET_ALL} > "

        try:
            user_input = input(prompt).strip()
            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0].lower()

            # --- BEFEHLSVERARBEITUNG ---

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
                    if handle_login():
                        print_menu_logged_in(session.account.username)

            elif command == "register":
                if session.is_active():
                    print("Bitte erst ausloggen.")
                else:
                    handle_register()

            elif command == "logout":
                if session.is_active():
                    session.end()
                    print(Fore.YELLOW + "Ausgeloggt." + Style.RESET_ALL)
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