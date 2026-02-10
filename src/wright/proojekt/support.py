import importlib.util
import logging
import os
import re
import sys
from enum import Enum
from pathlib import Path


class InvalidVersionError(Exception):
    """The version defined in the BUILD.py does not match semantic versioning."""
    pass


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
        except AttributeError as err:
            logging.warning(f"Unable to locate {fn} in {path}: {err}")
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


class Version(Enum):
    """Used to indicate which part of the semantic version to bump."""
    MAJOR = 0
    MINOR = 1
    PATCH = 2


def bump_version(build_file: str, semantic: Version = Version.PATCH) -> tuple[int, int, int] | None:
    """Open the BUILD.py file, look for a constant, VERSION, and try to bump the
    version number of the application.  Only works for semantic versioning."""
    with open(build_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    ret_value = None
    with open(build_file, "w", encoding="utf-8") as f:
        for line in lines:
            if not ret_value:
                version = _get_version(line)
                if version:
                    original, major, minor, patch = version
                    match semantic:
                        case Version.MAJOR:
                            major += 1
                        case Version.MINOR:
                            minor += 1
                        case Version.PATCH:
                            patch += 1

                    ret_value = (major, minor, patch)

                    f.write(line.replace(original, f'"{major}.{minor}.{patch}"'))

                    continue

            f.write(line)

    return ret_value


def _get_version(line: str) -> tuple[str, int, int, int] | None:
    """Looks at a string of text for a matching VERSION.  Used by bump_version."""
    match = re.compile(r'(?:export)?\s*VERSION\s*=\s*(["\'](\d)\.(\d)\.(\d)["\'])').match(line)
    if match:
        try:
            version = match.group(1)

            major = int(match.group(2))
            minor = int(match.group(3))
            patch = int(match.group(4))

            return version, major, minor, patch
        except IndexError:
            return None

    return None
