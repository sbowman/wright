import sh

from wright.proojekt import Proojekt


class OpenAPI:
    """
    Support creating operational documentation using Markdown documents and
    pandoc.
    """

    def __init__(self, project: Proojekt, generator: str = "swag"):
        self.project = project
        self._generator = generator
        self.general = None
        self.output = None
        self._version = None
        self._parseDependencies = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"There was a problem generating the OpenAPI documentation: {exc_val}")
            return False

        try:
            if self._generator == "swag":
                self.swag()
            else:
                print(f"Invalid generator value: {self._generator}")
                return False
        except Exception as e:
            print(f"Unable to generate the OpenAPI file: {e}")
            return False

        return True

    def parse_dependency(self):
        """
        Indicate the swag app should parse the Go package dependencies.
        """
        self._parseDependencies = True

    def version(self, value: str):
        """Indicate the output version of the OpenAPI docs.  Only 2.0 and 3.1 are supported."""
        if value == "3.1":
            self._version = value
        elif value != "2.0":
            raise ValueError(f"Invalid version: {value}")

    def swag(self):
        """Runs swag to generate OpenAPI documentation.  Requires the swag v2 binary."""
        args = ["init"]

        if self.general is not None:
            args.append("-g")
            args.append(self.general)

        if self.output is not None:
            args.append("-o")
            args.append(self.output)

        if self._version == "3.1":
            args.append("--v3.1")

        if self._parseDependencies:
            args.append("--parseDependency")

        process = sh.swag(*args, _iter="out", _err_to_out=True, _cwd=self.project.working_dir)
        for line in process:
            print(line.strip())


def swag(project: Proojekt):
    """Generate OpenAPI documentation for the Swag app (Go only)."""
    return OpenAPI(project, generator = "swag")
