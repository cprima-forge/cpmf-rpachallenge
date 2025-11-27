"""Side effect taxonomy and decorator for action functions.

This module provides a taxonomy of side effects that actions can have,
and a decorator to declare them. This helps learners understand the
I/O boundaries between pure functional code and effectful actions.
"""

from functools import wraps
from typing import Callable, Literal

Effect = Literal["none", "network", "filesystem", "dom_read", "dom_mutate"]


def side_effects(*effects: Effect) -> Callable:
    """Decorator to declare side effects on a function.

    Args:
        *effects: One or more effect types from the taxonomy:
            - "none": Pure function, no side effects
            - "network": HTTP request (GET, POST, etc.)
            - "filesystem": File read or write
            - "dom_read": Browser DOM query (non-mutating)
            - "dom_mutate": Browser DOM modification (click, fill, etc.)

    Returns:
        Decorator function that attaches side_effects metadata

    Example:
        ```python
        @side_effects("network", "filesystem")
        def fetch_excel(url: str) -> Path:
            '''Download Excel file.'''
            ...

        # Metadata accessible at runtime
        print(fetch_excel.side_effects)  # ["network", "filesystem"]
        ```
    """

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        wrapper.side_effects = list(effects)
        return wrapper

    return decorator
