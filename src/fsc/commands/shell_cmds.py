
import click
from fsc.assistant_shell import AiCodingAssistantShell

@click.command
def assistant_shell():
    """start an interactive assistant shell"""
    try:
        shell = AiCodingAssistantShell()
        shell.run()
    except Exception as e:
        print(f"Error starting assistant shell: {e}")
        
   
    