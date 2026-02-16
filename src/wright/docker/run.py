import sh

from wright.proojekt import Proojekt


class Runner:
    """Manages the Docker run process."""

    def __init__(self,
                 project: Proojekt,
                 container_name: str,
                 version: str = "latest",
                 rm: bool = True,
                 follow: bool = False):
        self.project = project
        self.container_name: str = container_name
        self.version: str = version
        self.rm: bool = rm
        self.follow: bool = follow
        self.env: dict[str, str] = {}
        self.ports: list[str] = []
        self._network: str | None = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"There was a problem configuring the Docker run: {exc_val}")
            return False

        try:
            self.run()
        except Exception as e:
            print(f"Unable to run the Docker image: {e}")
            return False

        return True

    def add_port(self, external: int, internal: int):
        self.ports.append(f"{external}:{internal}")

    def set_env(self, key: str, value: str):
        self.env[key] = value

    def network(self, name: str = None):
        """Set the network for the Docker run."""
        self._network = name

    def run(self):
        """Builds the Docker image using the docker binary and buildx."""
        args = [
            "run",
        ]

        if self.rm:
            args.append("--rm")

        if not self.follow:
            args.append("-d")

        for port in self.ports:
            args.append("-p")
            args.append(port)

        if self._network:
            args.append("--network")
            args.append(self._network)

        for key, value in self.env.items():
            args.append("-e")
            args.append(f"{key}={value}")

        args.append(f"{self.container_name}:{self.version}")

        process = sh.docker(*args, _iter="out", _err_to_out=True, _cwd=self.project.working_dir)
        for line in process:
            print(line.strip())


def run(project: Proojekt, container_name: str, version: str = "latest", rm: bool = True, follow: bool = False):
    """Run a Docker image using a with clause."""
    return Runner(project, container_name, version, rm=rm, follow=follow)
