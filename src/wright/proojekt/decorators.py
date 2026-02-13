import inspect
import logging
import os
from functools import wraps
from pathlib import Path
from typing import Callable

from .proojekt import Proojekt
from .support import load_file, current_path


def task(func):
    """Mark a function as a build task and inject the context."""
    caller_frame = inspect.stack()[1]
    caller_filename = caller_frame.filename
    working_dir = Path(os.path.abspath(caller_filename)).parent

    @wraps(func)
    def wrapper(*args, **kwargs):
        ctx = _get_ctx(args, kwargs)
        current_dir = None

        if _accepts_ctx_param(func):
            if not ctx:
                kwargs["ctx"] = Proojekt(working_dir)
            else:
                # "Push" the working dir of this task, so we call commands from
                # the right place.
                current_dir = ctx.working_dir
                ctx.working_dir = working_dir

        results = func(*args, **kwargs)

        # Reset the context's working dir
        if ctx and current_dir:
            ctx.working_dir = current_dir

        return results

    return wrapper


def sources(glob: str):
    """Mark a function as a build source."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if _accepts_ctx_param(func):
                ctx = _get_ctx(args, kwargs)
                if ctx is None:
                    raise Exception("Please declare a task before using sources")

                if Path(glob).is_absolute():
                    ctx.watch(glob)
                else:
                    ctx.watch(str(Path(ctx.working_dir / glob).absolute()))

            return func(*args, **kwargs)

        return wrapper

    return decorator


def depends(task_func: Callable):
    """Indicate the task depends on the given task, so run this task first."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            task_func_kwargs = _may_include_kwargs(task_func, kwargs)
            task_func(*args, **task_func_kwargs)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def target(name: str):
    """Set the target output for the build process."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ctx = _get_ctx(args, kwargs)
            if ctx is None:
                raise Exception("Please declare a task before setting the target")

            ctx.target = name

            return func(*args, **kwargs)

        return wrapper

    return decorator


def include(path: Path | str, name: str = None):
    """
    Load the build file from another path and include in the context.  By
    default uses the name of the path containing the build file as the name of
    the module in the Project, but that can be overridden using the name.

    If you provide a module name, it will attach the build to sys.modules with
    the given name."
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ctx = _get_ctx(args, kwargs)
            if ctx is None:
                raise Exception("Please declare a task before including other projects")

            p = Path(path)
            if p.is_dir():
                module_name = name or p.name
                module, _ = load_file(p / "BUILD.py", module_name=module_name, skip_sys_modules=True)
            else:
                module_name = name or p.parent.name
                module, _ = load_file(p, module_name=module_name, skip_sys_modules=True)

            if module_name in ctx:
                logging.warning(f"You are replacing {module_name} in the build context")

            ctx[module_name] = module

            return func(*args, **kwargs)

        return wrapper

    return decorator


def _accepts_ctx_param(func: Callable):
    sig = inspect.signature(func)
    return "ctx" in sig.parameters


def _may_include_kwargs(func: Callable, kwargs: dict) -> dict:
    """Check the signature of the wrapped function for arguments to inject."""
    sig = inspect.signature(func)
    has_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())

    if has_kwargs:
        return kwargs

    return {
        k: v for k, v in kwargs.items() if k in sig.parameters
    }

def _get_ctx(args, kwargs) -> Proojekt | None:
    """Look for the context (ctx) in the args or the kwargs."""
    for arg in args:
        if type(arg) is Proojekt:
            return arg

    for arg, value in kwargs.items():
        if "ctx" == arg:
            return value

    return None

