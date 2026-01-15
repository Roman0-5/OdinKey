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

def generate(length, uppercase, lowercase, digits, special, copy):
    #ruft PasswordGenerator auf
    service = PasswordGeneratorService()
    #mapping für unsere commands
    result = service.generate_password(
        length=length,
        use_uppercase=uppercase,
        use_lowercase=lowercase,
        use_digits=digits,
        use_special=special
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

