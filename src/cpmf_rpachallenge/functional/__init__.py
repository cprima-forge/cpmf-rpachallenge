"""Functional paradigm - pure transformations, composable data access.

This module provides the functional programming approach:
- Pure data sources (no side effects)
- Composable combinators
- Schema-driven parsing
"""

# Protocol
from .protocol import DataSource

# Schema
from .schema import Column, Parser, Schema

# Sources
from .sources import HtmlTableSource, XlsxSource

# Combinators
from .combinators import collect, filter_records, map_records

__all__ = [
    # Protocol
    "DataSource",
    # Schema
    "Column",
    "Schema",
    "Parser",
    # Sources
    "XlsxSource",
    "HtmlTableSource",
    # Combinators
    "filter_records",
    "map_records",
    "collect",
]
