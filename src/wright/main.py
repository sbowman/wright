import click
from pathlib import Path

from wright import proojekt


@click.command()
@click.option('--script', default='./BUILD.py', help="Build file to use")
@click.argument("command", default="build")
def run(script: Path, command: str):
    """Run a command in a build script"""
    proojekt.load_file(script, command)


if __name__ == '__main__':
    run()
