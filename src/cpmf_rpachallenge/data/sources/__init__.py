"""Data sources - generic implementations."""

from .html_table import HtmlTableSource
from .xlsx import XlsxSource, default_row_to_dict

__all__ = ["XlsxSource", "HtmlTableSource", "default_row_to_dict"]
