from types import ModuleType

from .support import check_dependencies


class Proojekt:
    """Helps builds track files that change to know when to build, test, etc."""

    def __init__(self):
        self.sources: list[str] = ["BUILD.py"]
        self.target: str | None = None
        self._modules: dict[str, ModuleType] = {}

    def __setitem__(self, module_name: str, module: ModuleType):
        """Set a module reference on the project."""
        self._modules[module_name] = module

    def __getitem__(self, module_name: str) -> ModuleType:
        """Fetch a module from the project."""
        return self._modules[module_name]

    def __getattr__(self, name):
        """Used to call a loaded module like `project.my_module`."""
        try:
            return self._modules[name]
        except KeyError:
            raise AttributeError(f"'Proojekt' object has no module or attribute named '{name}'")

    def __contains__(self, module_name: str) -> bool:
        """Has the module been loaded into the project?"""
        return module_name in self._modules

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
