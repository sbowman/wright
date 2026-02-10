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
