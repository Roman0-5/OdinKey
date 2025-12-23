import click

from src.cli.commands.generator import generate


@click.group()
@click.version_option(version='0.0.1', prog_name='OdinKey')
def cli():
    """
    OdinKey Password Manager CLI

    Secure password manager with CLI and GUI.
    """
    pass


cli.add_command(generate)
if __name__ == '__main__':
    cli()