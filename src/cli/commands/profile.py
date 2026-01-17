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
    service_name = input(Fore.LIGHTRED_EX + "! " + Style.RESET_ALL + "Service (z.B. HCW-Portal): ")
    if not service_name:
        print(Fore.RED + "Abbruch: Service Name ist Pflicht." + Style.RESET_ALL)
        return

    username = input(Fore.LIGHTRED_EX + "! " + Style.RESET_ALL + "Username/Email (z.B. Student-1): ")
    if not username:
        print(Fore.RED + "Abbruch: Username ist Pflicht." + Style.RESET_ALL)
        return

    url = input("  URL (z.B. https://portal.hcw.ac.at) [optional]: ")

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
            if copy_with_timeout(profile.password, timeout=180):
                print(f"{Fore.GREEN} Passwort wurde in die Zwischenablage kopiert!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}(Sicherheits-Feature: Zwischenablage leert sich in 3 Minuten){Style.RESET_ALL}")

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


def edit():
    """Bearbeitet ein bestehendes Profil."""
    print("\n--- Profil Bearbeiten ---")

    # 1. Suchen / ID abfragen
    search_term = input("Welches Profil suchen? (Name/Service): ").strip()
    if not search_term:
        return

    # Repository & Service holen
    profile_repo = PasswordProfileRepository(db_conn, session.get_master_key())

    # Wir nutzen die existierende Suchfunktion des Repositories
    profiles = profile_repo.search_profiles(session.account.id, search_term)

    if not profiles:
        print("Kein Profil gefunden.")
        return

    # Ergebnisse anzeigen
    print(f"\nGefundene Profile:")
    for p in profiles:
        print(f"[{p.id}] {p.service_name} | {p.username}")

    # 2. ID auswählen
    try:
        profile_id = int(input("\nBitte ID eingeben zum Bearbeiten: "))
    except ValueError:
        print("Ungültige Eingabe.")
        return

    # Das korrekte Profil aus der Liste picken
    target_profile = next((p for p in profiles if p.id == profile_id), None)

    if not target_profile:
        print("ID nicht in den Suchergebnissen.")
        return

    print(f"\nBearbeite: {target_profile.service_name}")
    print("(Lass das Feld leer, um den alten Wert zu behalten)")

    # 3. Neue Werte abfragen (mit Logik: Leer = Behalten)
    new_service = input(f"Service ({target_profile.service_name}): ").strip()
    if new_service: target_profile.service_name = new_service

    new_user = input(f"Username ({target_profile.username}): ").strip()
    if new_user: target_profile.username = new_user

    new_pw = getpass.getpass(f"Passwort (***): ").strip()
    if new_pw:
        target_profile.password = new_pw

    new_url = input(f"URL ({target_profile.url}): ").strip()
    if new_url: target_profile.url = new_url

    # 4. Speichern
    try:
        # Hier nutzen wir das lokale profile_repo
        profile_service = PasswordProfileService(profile_repo, None)
        profile_service.update_profile(target_profile)
        print(Fore.GREEN + "\n Profil erfolgreich aktualisiert!" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"\n Fehler beim Speichern: {e}" + Style.RESET_ALL)


def manage_menu():
    if not session.is_active():
        print(Fore.RED + "Zugriff verweigert." + Style.RESET_ALL)
        return

    while True:
        print(f"\n{Fore.CYAN}--- Passwortprofil Verwalten ---{Style.RESET_ALL}")
        print(" 1. Bearbeiten")
        print(" 2. Löschen")
        print(" 0. Zurück zum Hauptmenü")

        choice = input(f"{Fore.GREEN}Auswahl > {Style.RESET_ALL}").strip()

        if choice == '1':
            edit()  # Ruft die existierende edit-Funktion auf
            break  # Nach Abarbeitung zurück oder break entfernen um im Menü zu bleiben
        elif choice == '2':
            delete()  # Ruft die existierende delete-Funktion auf
            break
        elif choice == '0':
            break
        else:
            print(Fore.RED + "Ungültige Auswahl." + Style.RESET_ALL)