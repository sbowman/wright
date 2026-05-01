import logging
from pathlib import Path

import click

from wright import proojekt


# TODO:  I need a "wright tasks" to list the available tasks

@click.command()
@click.option('--script', default='./BUILD.py', help="Build file to use")
@click.argument("command", default="build")
def run(script: Path, command: str):
    """Run a command in a build script"""
    try:
        logging.basicConfig(level=logging.WARNING)
        proojekt.load_file(script, command)
    except AttributeError as e:
        logging.error(e)


if __name__ == '__main__':
    run()
