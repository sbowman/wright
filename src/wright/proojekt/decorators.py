import inspect
import logging
from functools import wraps
from pathlib import Path
from types import FunctionType

from .proojekt import Proojekt
from .support import load_file


def task(func):
    """Mark a function as a build task and inject the context."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        if "ctx" in sig.parameters and "ctx" not in kwargs:
            ctx = Proojekt()
            kwargs["ctx"] = ctx

        return func(*args, **kwargs)

    return wrapper


def sources(glob: str):
    """Mark a function as a build source."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "ctx" not in kwargs:
                raise Exception("Please declare a task before using sources")

            ctx: Proojekt = kwargs.get('ctx')
            ctx.watch(glob)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def depends(task_func):
    """Indicate the task depends on the given task, so run this task first."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            task_func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator

def target(name: str):
    """Set the target output for the build process."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "ctx" not in kwargs:
                raise Exception("Please declare a task before setting the target")

            ctx: Proojekt = kwargs.get('ctx')
            ctx.target = name

            return func(*args, **kwargs)

        return wrapper

    return decorator

def include(path: Path | str, name: str = None):
    """
    Load the build file from another path and include in the context.  By
    default uses the name of the path containing the build file as the name of
    the module in the Project, but that can be overridden using the name.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "ctx" not in kwargs:
                raise Exception("Please declare a task before including other projects")

            ctx: Proojekt = kwargs.get('ctx')

            p = Path(path)
            if p.is_dir():
                module, _ = load_file(p  / "BUILD.py", skip_sys_modules=True)
                module_name = p.name
            else:
                module, _ = load_file(p, skip_sys_modules=True)
                module_name = p.parent.name

            if name:
                module_name = name

            if module_name in ctx:
                logging.warning(f"You are replacing {module_name} in the build context")

            ctx[module_name] = module

            return func(*args, **kwargs)

        return wrapper

    return decorator