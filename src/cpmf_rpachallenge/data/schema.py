"""Minimal type-aware schema definitions.

Generic - no domain-specific imports.
"""

from dataclasses import dataclass
from typing import Any, Callable

Parser = Callable[[Any], Any]


@dataclass(frozen=True)
class Column:
    """Schema column definition with type information."""

    name: str
    py_type: type
    parser: Parser | None = None

    def parse(self, value: Any) -> Any:
        """Parse raw value according to column type."""
        if value is None:
            return None
        if self.parser:
            return self.parser(value)
        return self.py_type(value)


# Schema is just a list of columns - keep it simple
Schema = list[Column]
