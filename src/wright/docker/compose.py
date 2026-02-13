import sh


def up(composefile: str | None = None, detach: bool = True) -> bool:
    """Run docker compose up.  If already running, skips and returns false."""
    if running(composefile):
        return False

    args = ["compose"]

    if composefile:
        args.append("-f")
        args.append(composefile)

    args.append("up")

    if detach:
        args.append("-d")

    sh.docker(*args)
    return True


def down(composefile: str | None = None) -> bool:
    """Run docker compose down.  If compose is not running, returns false."""
    if not running(composefile):
        return False

    args = ["compose"]

    if composefile:
        args.append("-f")
        args.append(composefile)

    args.append("down")

    sh.docker(*args)
    return True


def logs(composefile: str | None = None, follow: bool = False):
    """Print the docker compose logs running in the background."""
    args = ["compose"]

    if composefile:
        args.append("-f")
        args.append(composefile)

    args.append("logs")

    if follow:
        args.append("-f")

    print("Running logs {}".format(args))
    sh.docker(*args, _out=True)


def running(composefile: str | None = None) -> bool:
    """Check if the Docker Compose instance is running."""
    args = ["compose"]

    if composefile:
        args.append("-f")
        args.append(composefile)

    args.append("ps")

    output = sh.docker(*args)
    return len(output.split("\n")) > 2
