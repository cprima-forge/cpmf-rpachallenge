"""DataSource protocol and functional combinators.

Generic - no domain-specific imports.
"""

from typing import Any, Callable, Iterable, Mapping, Protocol, TypeVar

T = TypeVar("T", bound=Mapping[str, Any])


class DataSource(Protocol[T]):
    """Protocol for data sources - functional, composable."""

    def load(self) -> Iterable[T]:
        """Yield records from the source."""
        ...


# Functional combinators - use consistent naming (always `predicate`)


def filter_records(
    source: DataSource[T],
    predicate: Callable[[T], bool],
) -> Iterable[T]:
    """Filter records from a source (lazy)."""
    for record in source.load():
        if predicate(record):
            yield record


def map_records(
    source: DataSource[T],
    transform: Callable[[T], T],
) -> Iterable[T]:
    """Transform records from a source (lazy)."""
    for record in source.load():
        yield transform(record)


def collect(source: DataSource[T]) -> list[T]:
    """Materialize source into list."""
    return list(source.load())
