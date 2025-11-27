"""DataSource protocol - functional, composable data access.

Generic - no domain-specific imports.
"""

from typing import Any, Iterable, Mapping, Protocol, TypeVar

T = TypeVar("T", bound=Mapping[str, Any])


class DataSource(Protocol[T]):
    """Protocol for data sources - functional, composable.

    Data sources are lazy iterables that yield records when load() is called.
    This protocol enables functional composition through combinators like
    filter_records() and map_records().
    """

    def load(self) -> Iterable[T]:
        """Yield records from the source.

        Returns:
            Iterable of records (typically dicts matching a schema)

        Note:
            This method should be lazy - it should not perform I/O until iteration begins.
        """
        ...
