"""RPAChallenge domain: schema, record type, and factory functions.

⚠️ DEPRECATED - Import from domain.records instead.

    Old (deprecated):
        from cpmf_rpachallenge.records import ChallengeRecord, from_xlsx, load_records

    New (recommended):
        from cpmf_rpachallenge.domain.records import ChallengeRecord, from_xlsx, load_records

This module is kept for backwards compatibility only.
"""

import warnings

from .domain.records import (
    ChallengeRecord,
    EXCEL_HEADER_MAP,
    FORM_FIELD_MAP,
    HTML_TABLE_HEADER_MAP,
    RPA_CHALLENGE_SCHEMA,
    from_xlsx,
    load_records,
)

# Issue deprecation warning on import
warnings.warn(
    "records.py is deprecated. Use 'from cpmf_rpachallenge.domain.records import ...' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ChallengeRecord",
    "RPA_CHALLENGE_SCHEMA",
    "FORM_FIELD_MAP",
    "EXCEL_HEADER_MAP",
    "HTML_TABLE_HEADER_MAP",
    "from_xlsx",
    "load_records",
]
