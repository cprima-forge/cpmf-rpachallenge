"""Actions layer - discrete I/O operations with declared side effects.

This module provides action functions that handle I/O boundaries:
- DOM operations (scrape_table_html)
- File system operations (read_excel)
- Pure transformations with no side effects (parse_html_table)

All actions are decorated with @side_effects() to declare their effects:
- none: Pure function, no side effects
- filesystem: Reads or writes to file system
- network: Makes network requests
- dom_read: Queries browser DOM
- dom_mutate: Modifies browser DOM
"""

from ._effects import Effect, side_effects
from .data import parse_html_table, read_excel, scrape_table_html

__all__ = [
    # Side effects taxonomy
    "side_effects",
    "Effect",
    # Data access actions
    "scrape_table_html",
    "read_excel",
    "parse_html_table",
]
