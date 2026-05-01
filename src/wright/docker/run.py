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
        """Runs the Docker container."""
        if running(container_name=self.container_name, version=self.version):
            return

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
    """Run a Docker container, if the container and version aren't already running."""
    return Runner(project, container_name, version, rm=rm, follow=follow)


def running(coupling: str = None, container_name: str = None, version: str = None):
    """Returns true if the coupling or container is running."""
    if coupling:
        filter_str = f"label=com.wsp.conduit.coupling={coupling}"
    elif container_name:
        tag = f":{version}" if version else ""
        filter_str = f"ancestor={container_name}{tag}"
    else:
        filter_str = None

    container_ids = sh.docker.ps("-q", "--filter", filter_str).strip().split()

    return len(container_ids) > 0


def stop(coupling: str = None, container_name: str = None, version: str = None):
    """Stop a Docker image by the coupling type or container tag."""
    if coupling:
        filter_str = f"label=com.wsp.conduit.coupling={coupling}"
    elif container_name:
        tag = f":{version}" if version else ""
        filter_str = f"ancestor={container_name}{tag}"
    else:
        filter_str = None

    if filter_str:
        container_ids = sh.docker.ps("-q", "--filter", filter_str).strip().split()

        if container_ids:
            sh.docker.stop(*container_ids)
