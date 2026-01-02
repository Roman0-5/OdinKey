import click
from src.cli.commands.auth import login, register, logout
from src.cli.commands.generator import generate


@click.group()
@click.version_option(version='0.0.1', prog_name='OdinKey')
def cli():
    """
    OdinKey Password Manager CLI
    """
    pass


# Alle Befehle
cli.add_command(login)
cli.add_command(register)  # Neu
cli.add_command(logout)  # Neu
cli.add_command(generate)

if __name__ == '__main__':
    cli()