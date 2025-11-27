"""Data sources - generic implementations."""

from .xlsx import XlsxSource
from .html_table import HtmlTableSource

__all__ = ["XlsxSource", "HtmlTableSource"]
