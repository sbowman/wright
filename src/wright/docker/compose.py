import sh

_cmd_docker = sh.Command("docker")


def up(composefile: str | None = None, detach: bool = True):
    """Run docker compose up."""
    args = ["compose"]

    if composefile:
        args.append("-f")
        args.append(composefile)

    args.append("up")

    if detach:
        args.append("-d")

    _cmd_docker(args)


def down(composefile: str | None = None):
    """Run docker compose down."""
    args = ["compose"]

    if composefile:
        args.append("-f")
        args.append(composefile)

    args.append("down")

    _cmd_docker(args)


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
    _cmd_docker(args, _out=True)
