import threading
import time
import click
import pyperclip
from colorama import Fore, Style

from src.services.password_generator_service import PasswordGeneratorService
"""
click.option Aufbau
Name (mind eines getrennt mit einem ','), Defaultwert, Helpausgabe
Bei den Namen kann man direkt eine Option einbauen mit '/',
hierbei ist Default True (links) oder False (rechts)
is_flag heißt dass es Optional ist
"""
service = PasswordGeneratorService()
def clear_clipboard_after_timeout(seconds):
    def clear():
        time.sleep(seconds)
        try:
            pyperclip.copy('')
            print(Fore.CYAN + "Passwort kann nicht mehr eingefügt werden"+ Style.RESET_ALL)
            print()
        except:
            pass
    thread = threading.Thread(target=clear, daemon=True)
    thread.start()
# helper methods
def ask_bool(prompt, default=True):
    """Hilfsfunktion für Ja/Nein Abfragen."""
    suffix = " [Y/n]" if default else " [y/N]"
    val = input(prompt + suffix + ": ").strip().lower()
    if not val:
        return default
    return val in ["y", "yes", "j", "ja"]


def ask_int(prompt: str, default: int, min_val: int = None, max_val: int = None) -> int:
    """Hilfsfunktion für Integer-Eingaben."""
    while True:
        response = input(f"{prompt} (Enter für {default}): ").strip()

        if not response:
            return default

        try:
            value = int(response)

            if min_val is not None and value < min_val:
                print(Fore.RED + f"✗ Minimum ist {min_val}" + Style.RESET_ALL)
                continue

            if max_val is not None and value > max_val:
                print(Fore.RED + f"✗ Maximum ist {max_val}" + Style.RESET_ALL)
                continue

            return value

        except ValueError:
            print(Fore.RED + "✗ Bitte eine Zahl eingeben" + Style.RESET_ALL)


def _display_result(result: dict):
    """Display generation result."""
    if result and result['success']:
        password = result['password']
        print("\n" + Fore.GREEN + "Passwort erflolgreich erstellt!" + Style.RESET_ALL)
        print("\n" + Fore.YELLOW + "Passwort:" + Style.RESET_ALL)
        print("  " + Fore.CYAN + password + Style.RESET_ALL)
        print(f"  Länge: {result['length']} Zeichen")

        if 'algorithm' in result:
            print(f"  Algorithmus: {result['algorithm']}")

        print()

    elif result:
        print("\n" + Fore.RED + f"✗ Fehler: {result['error']}" + Style.RESET_ALL)
def get_wordlist_size() -> int:
    return len(service.wordlist)
# logic
def generate_random(length, uppercase, lowercase, digits, special, copy):
    #ruft PasswordGenerator auf
    #mapping für unsere commands
    result = service.generate_password(
        length=length,
        use_uppercase=uppercase,
        use_lowercase=lowercase,
        use_digits=digits,
        use_special=special,
        algorithm='random'
    )

    if result['success']:
        password = result['password']

        print()
        print(Fore.GREEN + "Passwort wurde generiert!" + Style.RESET_ALL)
        print()
        print("  " + Fore.CYAN + password + Style.RESET_ALL)
        print()

        if copy:
            try:
                pyperclip.copy(password)
                print(Fore.YELLOW + f"Password kopiert für 3 Minuten!" + Style.RESET_ALL)
                print()

                clear_clipboard_after_timeout(180)
            except Exception as e:
                print(Fore.RED + f"Fehler: {e}" + Style.RESET_ALL)

    else:
        click.echo()
        click.echo(Fore.RED + f"✗ Error: {result['error']}" + Style.RESET_ALL)
        click.echo()
    return result
def generate_pronounceable(
        length: int = 12,
        use_digits: bool = True,
        use_special: bool = True,
        copy: bool = False,
) -> dict:
    result = service.generate_password(
        length=length,
        use_digits=use_digits,
        use_special=use_special,
        algorithm='pronounceable'
    )
    if copy and result['success']:
        pyperclip.copy(result['password'])
        print(Fore.YELLOW + f"Password kopiert für 3 Minuten!" + Style.RESET_ALL)
        clear_clipboard_after_timeout(180)

    return result
def generate_passphrase(
        num_words: int = 4,
        use_digits: bool = True,
        use_special: bool = True,
        copy: bool = False,
) -> dict:
    num_words = max(2, min(num_words, 8))
    result = service.generate_password(
        length=num_words * 5,
        use_digits=use_digits,
        use_special=use_special,
        algorithm='passphrase'
    )
    if copy and result['success']:
        pyperclip.copy(result['password'])
        print(Fore.YELLOW + f"Password kopiert für 3 Minuten!" + Style.RESET_ALL)
        clear_clipboard_after_timeout(180)
    return result

def generate_pattern(
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_special: bool = True,
        copy: bool = False,
) -> dict:
    result = service.generate_password(
        use_uppercase=use_uppercase,
        use_lowercase=use_lowercase,
        use_digits=use_digits,
        use_special=use_special,
        algorithm='pattern'
    )

    if copy and result['success']:
        pyperclip.copy(result['password'])
        print(Fore.YELLOW + f"Password kopiert für 3 Minuten!" + Style.RESET_ALL)
        clear_clipboard_after_timeout(180)

    return result
def generate_wildcard(
        template: str,
        copy: bool = False
) -> dict:
    result = service.generate_with_wildcard(template)
    if copy and result['success']:
        pyperclip.copy(result['password'])
        print(Fore.YELLOW + f"Password kopiert für 3 Minuten!" + Style.RESET_ALL)
        clear_clipboard_after_timeout(180)
    return result

# TUI stuff
def generate(): #FMR5
    """Main generator menu - choose algorithm."""
    print("\n" + Fore.CYAN + "Willkommen im Passwort Generator Menü!" + Style.RESET_ALL)

    print("\n" + Fore.YELLOW + "Bitte wähle einen Algorithmus:" + Style.RESET_ALL)
    print(f"  {Fore.GREEN}1{Style.RESET_ALL} - Random       (Zufällige Zeichen)")
    print(f"  {Fore.GREEN}2{Style.RESET_ALL} - Pronounceable (Aussprechbar)")
    print(f"  {Fore.GREEN}3{Style.RESET_ALL} - Passphrase    (Mehrere Wörter) *")
    print(f"  {Fore.GREEN}4{Style.RESET_ALL} - Pattern       (Strukturiert)")
    print(f"  {Fore.GREEN}5{Style.RESET_ALL} - Wildcard      (Eigenes Template)") #FMR6

    choice = input("\n" + Fore.CYAN + "Algorithmus (1-5, Enter für 1): " + Style.RESET_ALL).strip()

    if choice == '1' or not choice:
        gen_random_menu()
    elif choice == '2':
        gen_pronounceable_menu()
    elif choice == '3':
        gen_passphrase_menu()
    elif choice == '4':
        gen_pattern_menu()
    elif choice == '5':
        gen_wildcard_menu()
    else:
        print(Fore.RED + "Ungültige Auswahl" + Style.RESET_ALL)


def gen_random_menu():
    """Interactive menu for random password."""
    print("\n" + Fore.CYAN + "--- Random Password ---" + Style.RESET_ALL)

    length = ask_int("Länge", default=16, min_val=8, max_val=64)
    use_upper = ask_bool("Großbuchstaben?", default=True)
    use_lower = ask_bool("Kleinbuchstaben?", default=True)
    use_digits = ask_bool("Ziffern?", default=True)
    use_special = ask_bool("Sonderzeichen?", default=False)
    copy = ask_bool("In Zwischenablage kopieren?", default=False)

    result = generate_random(
        length=length,
        uppercase=use_upper,
        lowercase=use_lower,
        digits=use_digits,
        special=use_special,
        copy=copy
    )

    _display_result(result)


def gen_pronounceable_menu():
    """Interactive menu for pronounceable password."""
    print("\n" + Fore.CYAN + "--- Pronounceable Password ---" + Style.RESET_ALL)

    length = ask_int("Länge", default=12, min_val=6, max_val=32)
    use_digits = ask_bool("Ziffern anhängen?", default=True)
    use_special = ask_bool("Sonderzeichen anhängen?", default=True)
    copy = ask_bool("In Zwischenablage kopieren?", default=False)

    result = generate_pronounceable(
        length=length,
        use_digits=use_digits,
        use_special=use_special,
        copy=copy
    )

    _display_result(result)


def gen_passphrase_menu():
    """Interactive menu for passphrase."""
    print("\n" + Fore.CYAN + "--- Passphrase (XKCD-Style) ---" + Style.RESET_ALL)
    print(Fore.YELLOW + f"Wordlist: {get_wordlist_size()} Wörter verfügbar" + Style.RESET_ALL)

    num_words = ask_int("Anzahl Wörter", default=4, min_val=2, max_val=8)
    copy = ask_bool("In Zwischenablage kopieren?", default=False)

    result = generate_passphrase(
        num_words=num_words,
        use_digits=True,
        use_special=True,
        copy=copy
    )

    _display_result(result)


def gen_pattern_menu():
    """Interactive menu for pattern password."""
    print("\n" + Fore.CYAN + "--- Pattern Password ---" + Style.RESET_ALL)

    use_upper = ask_bool("Großbuchstaben?", default=True)
    use_lower = ask_bool("Kleinbuchstaben?", default=True)
    use_digits = ask_bool("Ziffern?", default=True)
    use_special = ask_bool("Sonderzeichen?", default=True)
    copy = ask_bool("In Zwischenablage kopieren?", default=False)

    result = generate_pattern(
        use_uppercase=use_upper,
        use_lowercase=use_lower,
        use_digits=use_digits,
        use_special=use_special,
        copy=copy
    )

    _display_result(result)


def gen_wildcard_menu():
    """Interactive menu for wildcard template."""
    print("\n" + Fore.CYAN + "--- Wildcard Template ---" + Style.RESET_ALL)
    print(f"\n{Fore.YELLOW}Wildcards:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}#{Style.RESET_ALL} - Ziffer (0-9)")
    print(f"  {Fore.GREEN}@{Style.RESET_ALL} - Buchstabe (a-z, A-Z)")
    print(f"  {Fore.GREEN}?{Style.RESET_ALL} - Beliebiges Zeichen (Buchstabe + Ziffer)")
    print(f"  {Fore.GREEN}!{Style.RESET_ALL} - Sonderzeichen")

    print(f"\n{Fore.YELLOW}Beispiel:{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}OdinKey-####-@@@@{Style.RESET_ALL}  → OdinKey-8374-Kfwq")

    template = input(f"\n{Fore.CYAN}Template: {Style.RESET_ALL}").strip()

    if not template:
        print(Fore.RED + "Template ist leer" + Style.RESET_ALL)
        return

    copy = ask_bool("In Zwischenablage kopieren?", default=False)

    result = generate_wildcard(template=template, copy=copy)

    _display_result(result)


# testing stuff
if __name__ == '__main__':
    print("=== Generator Command Tests ===\n")

    # Test 1: Random
    print("1. Random:")
    result = generate_random(length=16, uppercase=True, lowercase=True, digits=True, special=True, copy=False)
    #        ^^^^^^^^^^^^^^ Lokale Funktion!
    if result['success']:
        print(f"   {result['password']}\n")

    # Test 2: Pronounceable
    print("2. Pronounceable:")
    result = generate_pronounceable(length=12, use_digits=True, use_special=True, copy=False)
    if result['success']:
        print(f"   {result['password']}\n")

    # Test 3: Passphrase
    print("3. Passphrase:")
    result = generate_passphrase(num_words=4, use_digits=True, use_special=True, copy=False)
    if result['success']:
        print(f"   {result['password']}\n")

    # Test 4: Pattern
    print("4. Pattern:")
    result = generate_pattern(use_uppercase=True, use_lowercase=True, use_digits=True, use_special=True, copy=False)
    if result['success']:
        print(f"   {result['password']}\n")

    # Test 5: Wildcard
    print("5. Wildcard:")
    result = generate_wildcard("OdinKey-####-@@@@", copy=False)
    if result['success']:
        print(f"   {result['password']}\n")

    print("✓ All tests completed!")