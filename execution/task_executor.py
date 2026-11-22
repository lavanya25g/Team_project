"""Execute a callable task with validated arguments."""

from typing import Any, Callable, Dict, Optional


class TaskExecutionError(Exception):
    """Raised when the requested task raises an exception."""


def execute_task(
    function: Callable[..., Any],
    args: tuple = (),
    kwargs: Optional[Dict[str, Any]] = None,
) -> Any:
    """Execute ``function(*args, **kwargs)`` and return its result."""
    if not callable(function):
        raise TypeError("Task must be a callable function.")
    if not isinstance(args, tuple):
        raise TypeError("Arguments must be provided as a tuple.")
    if kwargs is None:
        kwargs = {}
    if not isinstance(kwargs, dict):
        raise TypeError("Keyword arguments must be a dictionary.")

    try:
        return function(*args, **kwargs)
    except Exception as error:
        raise TaskExecutionError(
            f"Task execution failed: {type(error).__name__}: {error}"
        ) from error
