import sys
from functools import wraps

from wright.proojekt import Proojekt


def task(func):
    """Mark a function as a build task."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get('ctx') is None:
            ctx = Proojekt()
            kwargs["ctx"] = ctx

        return func(*args, **kwargs)

    return wrapper


def sources(glob: str):
    """Mark a function as a build source."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ctx: Proojekt = kwargs.get('ctx')
            ctx.watch(glob)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def depends(task):
    """Indicate the task depends on the given task, so run this task first."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            task(*args, **kwargs)

            return func(*args, **kwargs)

        return wrapper

    return decorator
