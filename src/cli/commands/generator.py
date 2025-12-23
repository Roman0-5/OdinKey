import click
from colorama import Fore, Style
from src.services.password_generator_service import PasswordGeneratorService

"""
click.option Aufbau
Name (mind eines getrennt mit einem ','), Defaultwert, Helpausgabe
Bei den Namen kann man direkt eine Option einbauen mit '/',
hierbei ist Default True (links) oder False (rechts)
is_flag heißt dass es Optional ist
"""
@click.command()
@click.option('--length', '--lgth', '-l', default=8, help='Password length (8-128)')
@click.option('--uppercase/--nouppercase', '--uprcase/--nouprcase', default=True, help='Include uppercase letters')
@click.option('--lowercase/--nolowercase', '--lwrcase/--nolwrcase', default=True, help='Include lowercase letters')
@click.option('--digits/--nodigits', '--dgt/--nodgt', default=True, help='Include digits')
@click.option('--special/--nospecial', '--spcl/--nospcl', default=False, help='Include special characters')
@click.option('--copy', '-c', is_flag=True, help='Copy password to clipboard')
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

        click.echo() # Konsolenausgabe was in der Klammer steht, in dem Fall leer
        click.echo(Fore.GREEN + "Password generated successfully!" + Style.RESET_ALL)
        click.echo()
        click.echo("  " + Fore.CYAN + password + Style.RESET_ALL)
        click.echo()

        if copy:
            try:
                import pyperclip
                pyperclip.copy(password)
                click.echo(Fore.YELLOW + "Password copied to clipboard for 10 Minutes!" + Style.RESET_ALL)
                click.echo()
            except ImportError:
                click.echo(Fore.RED + "pyperclip not installed (pip install pyperclip)" + Style.RESET_ALL)
                click.echo()

    else:
        click.echo()
        click.echo(Fore.RED + f"✗ Error: {result['error']}" + Style.RESET_ALL)
        click.echo()


