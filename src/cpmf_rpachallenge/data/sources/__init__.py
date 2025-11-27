"""Data sources - generic implementations."""

from .xlsx import XlsxSource, default_row_to_dict

__all__ = ["XlsxSource", "default_row_to_dict"]
