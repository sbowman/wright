from typing import Any

import sh

_cmd_docker = sh.Command("docker")


class Builder:
    """Manages the Docker build process, leveraging buildx."""

    def __init__(self, container_name: str, version: str = "latest"):
        self.dockerfile: str = "Dockerfile"
        self.container_name: str = container_name
        self.version: str = version
        self._build_args: dict[str, Any] = {}

        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"There was a problem constructing the Docker build: {exc_val}")
            return False

        try:
            self.build()
        except Exception as e:
            print(f"Unable to build the Docker image: {e}")
            return False

        return True

    def build_arg(self, key: str, value: Any):
        self._build_args[key] = value

    def build(self):
        """Builds the Docker image using the docker binary and buildx."""
        args = [
            "buildx",
            "build",
            "--platform", "linux/amd64",
            "--tag", f"{self.container_name}:{self.version}",
            "--file", self.dockerfile
        ]

        for arg, value in self._build_args.items():
            args.append("--build-arg")
            args.append(f"{arg}={value}")

        args.append(".")
        _cmd_docker(*args)


def build(container_name: str, version: str = "latest") -> Builder:
    """
    Build a Docker image from the given dockerfile.  Expects a container name
    like `ghcr.io/emu-wsp-internal-repos/postgres`.  The version will be
    appended to the container name.

    Meant to be wrapped in a "with" statement, and the Docker container will be
    built at the end, provided there are no errors in the with clause:

        with Builder("ghcr.io/my-org/my-app") as image:
            image.version = "1.17.3"
            image.build_arg("SAMPLE", "this is a test")

    """
    return Builder(container_name, version)
