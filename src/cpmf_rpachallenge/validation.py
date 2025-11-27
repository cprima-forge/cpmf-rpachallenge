"""Validation utilities for rpachallenge.com Excel data.

⚠️ DEPRECATED - Import from domain.validation instead.

    Old (deprecated):
        from cpmf_rpachallenge.validation import DataValidator, DataValidationResult

    New (recommended):
        from cpmf_rpachallenge.domain.validation import DataValidator, DataValidationResult

This module is kept for backwards compatibility only.
"""

import warnings

from .domain.validation import (
    DataValidationResult,
    DataValidator,
    FieldError,
    RecordValidationResult,
)

# Issue deprecation warning on import
warnings.warn(
    "validation.py is deprecated. Use 'from cpmf_rpachallenge.domain.validation import ...' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "DataValidator",
    "DataValidationResult",
    "RecordValidationResult",
    "FieldError",
]
