"""Functional combinators for composable data transformations.

All combinators return DataSource (not Iterable) to enable chaining:
    filtered = filter_records(source, pred1)
    double_filtered = filter_records(filtered, pred2)  # Works!

Generic - no domain-specific imports.
"""

from typing import Callable, Iterable, Mapping, TypeVar, Any

from .protocol import DataSource

T = TypeVar("T", bound=Mapping[str, Any])


class FilteredSource(DataSource[T]):
    """DataSource wrapper that applies a predicate filter.

    This wrapper enables composability by returning a DataSource
    instead of a plain Iterable.
    """

    def __init__(self, source: DataSource[T], predicate: Callable[[T], bool]):
        """Initialize filtered source.

        Args:
            source: Input DataSource
            predicate: Function returning True for records to keep
        """
        self._source = source
        self._predicate = predicate

    def load(self) -> Iterable[T]:
        """Yield only records that pass the predicate.

        Yields:
            Records where predicate(record) is True
        """
        for record in self._source.load():
            if self._predicate(record):
                yield record


class MappedSource(DataSource[T]):
    """DataSource wrapper that applies a transformation.

    This wrapper enables composability by returning a DataSource
    instead of a plain Iterable.
    """

    def __init__(self, source: DataSource[T], transform: Callable[[T], T]):
        """Initialize mapped source.

        Args:
            source: Input DataSource
            transform: Function to apply to each record
        """
        self._source = source
        self._transform = transform

    def load(self) -> Iterable[T]:
        """Yield transformed records.

        Yields:
            Records after applying transform function
        """
        for record in self._source.load():
            yield self._transform(record)


# Public API


def filter_records(source: DataSource[T], predicate: Callable[[T], bool]) -> DataSource[T]:
    """Filter records from source (lazy, composable).

    Args:
        source: Input DataSource
        predicate: Function returning True for records to keep

    Returns:
        New DataSource that yields only matching records.
        Lazy - predicate applied during iteration.

    Example:
        ```python
        # Composable - returns DataSource
        managers = filter_records(source, lambda r: r["role"] == "Manager")
        senior = filter_records(managers, lambda r: "Senior" in r["role"])
        results = collect(senior)
        ```
    """
    return FilteredSource(source, predicate)


def map_records(source: DataSource[T], transform: Callable[[T], T]) -> DataSource[T]:
    """Transform records from source (lazy, composable).

    Args:
        source: Input DataSource
        transform: Function to apply to each record

    Returns:
        New DataSource that yields transformed records.
        Lazy - transform applied during iteration.

    Example:
        ```python
        # Add full_name field
        enriched = map_records(
            source,
            lambda r: {**r, "full_name": f"{r['first_name']} {r['last_name']}"}
        )
        results = collect(enriched)
        ```
    """
    return MappedSource(source, transform)


def collect(source: DataSource[T]) -> list[T]:
    """Materialize source into list.

    Args:
        source: Input DataSource

    Returns:
        List containing all records from source.
        Forces evaluation of lazy sources.

    Example:
        ```python
        source = from_xlsx("data.xlsx")
        filtered = filter_records(source, lambda r: r["active"])
        records = collect(filtered)  # Materialize
        ```
    """
    return list(source.load())
