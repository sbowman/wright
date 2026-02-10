from .support import check_dependencies


class Proojekt:
    """Helps builds track files that change to know when to build, test, etc."""

    def __init__(self):
        self.sources: list[str] = ["BUILD.py"]
        self.target: str | None = None

    def watch(self, glob: str):
        """Append a glob to watch for changes.  The files included by the glob
        will inform Wright whether or not to rebuild the binary."""
        self.sources.append(glob)

    def rewatch(self, glob: str):
        """Empties out the source files we're watching, including the defaults,
        to completely replace them."""
        self.sources = [glob]

    def should_run(self):
        """Returns true if the watchable dependencies change."""
        return check_dependencies(self.sources, self.target)
