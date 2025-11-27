"""Generic data access abstractions.

This module is domain-agnostic and can be reused across webapp packages.
No rpachallenge-specific imports allowed here.
"""

from .protocol import DataSource, collect, filter_records, map_records
from .schema import Column, Parser, Schema
from .sources import XlsxSource

__all__ = [
    # Protocol
    "DataSource",
    # Schema
    "Column",
    "Schema",
    "Parser",
    # Sources
    "XlsxSource",
    # Combinators
    "filter_records",
    "map_records",
    "collect",
]
