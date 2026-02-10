from .build import App

def app(module: str = None):
    """Creates a new Go app project to build.  Defaults to the module name in
    the golang.mod file."""
    return App(module=module)


def rm(module: str = None):
    """Deletes the default Go target binary for the project."""
    App(module=module).rm()
