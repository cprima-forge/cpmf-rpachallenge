"""Domain layer - business logic, schemas, and domain models.

This module provides domain-specific types and business logic:
- Records and schemas (ChallengeRecord, RPA_CHALLENGE_SCHEMA)
- Validation rules (DataValidator)
- Result parsing (Results, ResultData)
- Readiness checks (ReadinessCheck)
- Page selectors (Pages, ChallengePage, DataTablePage)
"""

from .readiness import ReadinessCheck, ReadinessResult
from .records import (
    ChallengeRecord,
    EXCEL_HEADER_MAP,
    FORM_FIELD_MAP,
    HTML_TABLE_HEADER_MAP,
    RPA_CHALLENGE_SCHEMA,
    from_xlsx,
    load_records,
)
from .results import ResultData, Results
from .selectors import Pages
from .validation import (
    DataValidationResult,
    DataValidator,
    FieldError,
    RecordValidationResult,
)

__all__ = [
    # Records and schemas
    "ChallengeRecord",
    "RPA_CHALLENGE_SCHEMA",
    "FORM_FIELD_MAP",
    "EXCEL_HEADER_MAP",
    "HTML_TABLE_HEADER_MAP",
    "from_xlsx",
    "load_records",
    # Validation
    "DataValidator",
    "DataValidationResult",
    "RecordValidationResult",
    "FieldError",
    # Results
    "Results",
    "ResultData",
    # Readiness
    "ReadinessCheck",
    "ReadinessResult",
    # Selectors
    "Pages",
]
