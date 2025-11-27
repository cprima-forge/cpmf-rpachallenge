"""Data sources - generic implementations."""

from .xlsx import XlsxSource, default_row_to_dict

# HtmlTableSource requires Playwright (optional dependency)
# Import it only when needed via lazy import in records.py

__all__ = ["XlsxSource", "default_row_to_dict"]
