import sys
import logging
from pathlib import Path

import sh

from wright.proojekt import Proojekt

class GolangModuleNotFoundError(Exception):
    """Raised when the Go module is not found."""
    pass


class App:
    def __init__(self, project: Proojekt, module: str | None = None):
        if module:
            self.module = module
        else:
            self.module = _get_module_name(project.working_dir / "go.mod")

        if not self.module:
            raise GolangModuleNotFoundError()

        self.proojekt = project
        self.proojekt.watch("**/*.go")
        self.proojekt.target = project.target or project.working_dir / _get_target_name(self.module)

        self.vars: dict[str, str] = {}
        self.ldflags: list[str] = []

    def sources(self, glob: str):
        """Add a file or pattern of files to watch for changes before compiling."""
        self.proojekt.watch(glob)

    def target(self, target: str | None = None) -> str | None:
        """Set or get the Go build target.  Defaults to the module basename."""
        if target:
            if Path(target).is_absolute():
                self.proojekt.target = target
            else:
                self.proojekt.target = str(self.proojekt.working_dir / target)

        return self.proojekt.target

    def var(self, name: str, value: str):
        """Set an embedded variable, using -ldflags when building the Go app."""
        self.vars[name] = value

    def release(self, production: bool = True):
        """Generate a binary without debug information if production is true."""
        if production:
            self.ldflags.append("-w")
            self.ldflags.append("-s")

    def changed(self) -> bool:
        """Have any of the watched files changed?"""
        return self.proojekt.should_run()

    def compile(self) -> App:
        """Compile a Go application using `golang build` if any of the watched
        files have changed."""
        if self.changed():
            args: list[str] = ["build"]

            if self.vars:
                for key, value in self.vars.items():
                    self.ldflags.append("-X")
                    self.ldflags.append("'{}/{}={}'".format(self.module, key, value))

            if self.ldflags:
                args.append("-ldflags")
                args.append(" ".join(self.ldflags))

            if self.proojekt.target:
                args.append("-o")
                args.append(self.proojekt.target)

            try:
                sh.go(*args, _out=True, _cwd=self.proojekt.working_dir)
            except Exception as err:
                logging.error(f"Error compiling: {err}")
                sys.exit(1)

        return self

    def test(self) -> App:
        """Run go test ./... to test all the packages in the Go project."""
        try:
            sh.go("test", "./...")
        except Exception as err:
            logging.error(f"Error running test: {err}")
            sys.exit(1)

        return self

    def run(self, *args):
        """Run the Go binary, i.e. the target."""
        print("Working dir is: {}".format(self.proojekt.working_dir))
        cmd = sh.Command(self.proojekt.target, search_paths=[self.proojekt.working_dir])
        try:
            output = cmd(*args, _iter="out", _err_to_out=True, _cwd=self.proojekt.working_dir)
            for line in output:
                print(line.strip())

            sys.exit(output.exit_code)
        except Exception as err:
            logging.error(f"Error running binary: {err}")
            sys.exit(1)

    def rm(self) -> App:
        """Removes the target binary, i.e. performs a clean.  If the target does
        not exist, the request is quietly ignored."""
        try:
            Path(self.target()).unlink()
        except FileNotFoundError:
            # It's ok if the file doesn't exist
            pass

        return self


def _get_module_name(file_path: Path) -> str | None:
    """Get the module name out of a golang.mod file.  Returns None if the module is
    undefined."""
    try:
        print("Looking in {}". format(file_path))
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if line.startswith("module"):
                    parts = line.split()
                    if len(parts) > 1:
                        return parts[1]

    except FileNotFoundError:
        return None

    return None


def _get_target_name(module_name: str) -> str | None:
    return Path(module_name).name
