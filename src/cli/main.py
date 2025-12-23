"""
CLI Main Setup
Registriert alle Commands Gruppen 
"""
import click

#from cli.commands.auth_commands import
#from cli.commands.profile_commands import
#from cli.commands.generator_commands import

@click.group()
def cli():
    pass
#cli.add_command(auth)
#cli.add_command(profile)
#cli.add_command(generate)