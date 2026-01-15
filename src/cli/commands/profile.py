import getpass
import sqlite3
from colorama import Fore, Style

from src.core.session import session
from src.database.connection import db as db_conn
from src.core.password_profile import PasswordProfile
from src.database.password_profile_repository import PasswordProfileRepository
from src.services.password_profile_service import PasswordProfileService
from src.services.master_account_service import MasterAccountService
from src.database.repository import MasterAccountRepository
from src.utils.clipboard import copy_with_timeout

repo = MasterAccountRepository(db_conn)
service = MasterAccountService(repo)

def ask_bool(prompt, default=True):
    """Helper for yes/no questions."""
    suffix = " [Y/n]" if default else " [y/N]"
    val = input(prompt + suffix + ": ").strip().lower()
    if not val:
        return default
    return val in ["y", "yes", "j", "ja"]
def add():
    """Fügt ein neues Passwort hinzu und verschlüsselt es."""
    if not session.is_active():
        print(Fore.RED + "Zugriff verweigert. Bitte einloggen" + Style.RESET_ALL)
        return

    print("\n--- Neues Passwort anlegen ---")
    service_name = input(Fore.LIGHTRED_EX + "! " + Style.RESET_ALL + "Service (z.B. Google): ")
    if not service_name:
        print(Fore.RED + "Abbruch: Service Name ist Pflicht." + Style.RESET_ALL)
        return

    username = input(Fore.LIGHTRED_EX + "! " + Style.RESET_ALL + "Username/Email: ")
    if not username:
        print(Fore.RED + "Abbruch: Username ist Pflicht." + Style.RESET_ALL)
        return

    url = input("URL (optional): ")

    print(Fore.LIGHTRED_EX + "! " + Style.RESET_ALL + "Passwort: ", end="", flush=True)
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

        # 1. Repository initialisieren (braucht Master Key zum Verschlüsseln)
        repo_profile = PasswordProfileRepository(db_conn, session.get_master_key())

        # 2. Service erstellen (Backend-Lösung)
        # Wir übergeben 'service' (MasterAccountService) für eventuelle Checks
        profile_service = PasswordProfileService(repo_profile, service)

        # 3. Speichern über Service
        profile_service.create_profile(profile)

        print(Fore.GREEN + f"Eintrag für '{service_name}' erfolgreich verschlüsselt gespeichert!" + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + f"Fehler beim Speichern: {e}" + Style.RESET_ALL)


def list_passwords(interactive=True):
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
                print(f"{Fore.GREEN} Passwort wurde in die Zwischenablage kopiert!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}(Sicherheits-Feature: Zwischenablage leert sich in 60 Sek.){Style.RESET_ALL}")

            if ask_bool("Soll das Passwort zusätzlich angezeigt werden?", default=False):
                print(f"Passwort: {Fore.RED}{profile.password}{Style.RESET_ALL}")

            input("Drücke Enter um fortzufahren...")
        else:
            print(Fore.RED + "Eintrag nicht gefunden oder kein Zugriff." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + f"Fehler beim Entschlüsseln: {e}" + Style.RESET_ALL)


def delete():
    """Löscht einen Eintrag nach erneuter Passwort-Bestätigung (Über Backend-Service)."""
    if not session.is_active():
        return

    conn = db_conn.connect()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, service_name, username FROM password_profiles WHERE user_id = ?",
            (session.account.id,)
        )
        rows = cursor.fetchall()

        if not rows:
            print(Fore.YELLOW + "Keine Passwörter gefunden." + Style.RESET_ALL)
            return

        print(f"\n{Fore.CYAN}{'ID':<5} {'Service':<20} {'Username'}{Style.RESET_ALL}")
        print("-" * 45)
        for row in rows:
            print(f"{row['id']:<5} {row['service_name'] or '':<20} {row['username'] or ''}")
        print("-" * 45)
    finally:
        conn.close()

    id_str = input("\nID löschen (oder Enter): ").strip()
    if not id_str:
        return

    try:
        profile_id = int(id_str)

        print(Fore.YELLOW + "Master-Passwort erforderlich" + Style.RESET_ALL)
        print("Master-Passwort: ", end="", flush=True)
        conf_pw = getpass.getpass("")

        repo_profile = PasswordProfileRepository(db_conn, session.get_master_key())
        profile_service = PasswordProfileService(repo_profile, service)

        profile_service.delete_profile_securely(
            profile_id=profile_id,
            username=session.account.username,
            password_attempt=conf_pw
        )
        print(Fore.GREEN + f"Eintrag {profile_id} gelöscht." + Style.RESET_ALL)

    except PermissionError:
        print(Fore.RED + "Falsches Passwort." + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + "Ungültige ID." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Fehler: {e}" + Style.RESET_ALL)


def search():
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
            print(f"{p.id:<5} {p.service_name or '':<20} {p.username or '':<25} {p.url or ''}")
        print("-" * 70)

        # Direkt anbieten zu entschlüsseln
        choice = input("\nID zum Entschlüsseln (oder Enter für zurück): ").strip()
        if choice and choice.isdigit():
            reveal_password(int(choice))

    except Exception as e:
        print(Fore.RED + f"Such-Fehler: {e}" + Style.RESET_ALL)