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

                clear_clipboard_after_timeout(5)
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