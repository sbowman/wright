import importlib.util
import logging
import os
import sys
from pathlib import Path


def load_file(path: Path, fn: str):
    """
    Treats BUILD.py like a custom script for the wright tool.  Load the BUILD.py
    file and run the indicated function (build, test, run, package, etc.).  If
    successful, returns the result of the function.  If the BUILD.py file or
    function does not exist, logs a warning and returns None.

    :param path: the path to the BUILD.py or other build file
    :param fn: the name of the function to run in the BUILD.py file
    :return: the results of calling the function in the BUILD.py file
    """

    module_name = "buildfile"

    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
    except FileNotFoundError:
        logging.warning(f"No build file found at {path}")
        return None

    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        try:
            func = getattr(module, fn)
            return func()
        except AttributeError:
            logging.warning(f"Unable to locate {fn} in {path}")
            return None

    logging.warning(f"Build file {path} does not appear to be a Python module")
    return None


def check_dependencies(globs: list[str], reference_file: str) -> bool:
    """Compare the timestamp of the files matching the pattern with the
    timestamp of the reference file to determine if the files have changed since
    the reference file.  Returns true if the reference file doesn't exist or the
    files have changed.

    :param globs: an array of files to check
    :param reference_file: the file to compare the other files against"""

    reference = Path(reference_file)
    if not reference.exists():
        return True

    ref_mtime = reference.stat().st_mtime

    for glob in globs:
        for file in _parse_glob(glob):
            file_mtime = file.stat().st_mtime

            if file_mtime >= ref_mtime:
                return True

    return False


# def _match_files(pattern: str):
#     for glob in _globs(pattern):
#         for file in _parse_glob(glob):
#             yield file


# def _globs(pattern: str) -> list[str]:
#     """Return the individual dependency patterns split by comma or space.  Note
#     you may use a space in a path if you surround it by quotation marks."""
#     commas_or_spaces = pattern.replace(",", " ")
#     return shlex.split(commas_or_spaces)


def _parse_glob(glob: str):
    """If the glob is an absolute path, parse into the root path and the glob.
    If it's a relative glob or path, just return the current path and the glob."""
    path = Path(glob)

    if path.is_absolute():
        root_parts = []
        glob_parts = []
        found_glob = False

        for part in path.parts:
            if "*" in part or found_glob:
                glob_parts.append(part)
                found_glob = True
            else:
                root_parts.append(part)

        yield from Path(*root_parts).glob("/".join(glob_parts))

    else:
        yield from Path(os.getcwd()).glob(glob)


def is_env(var: str, value: str = "true") -> bool:
    """Returns true if the var environment variable exists and is set to the
    given value.  If the value is not supplied, assumes a true or false value."""
    env = os.getenv(var)
    return env and env.casefold() == value.casefold()
