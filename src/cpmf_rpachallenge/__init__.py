"""Domain SDK for rpachallenge.com automation.

Architecture:
    - RPAChallengeClient: Domain-facing API (backend-agnostic)
    - Backends: Driver implementations (Playwright, API, Mixed)

Usage:
    from cpmf_rpachallenge import RPAChallengeClient, PlaywrightBackend

    backend = PlaywrightBackend(page)
    client = RPAChallengeClient(backend=backend)
    result = await client.run_async()

Data Access (new API):
    from cpmf_rpachallenge import fetch_challenge_excel, from_xlsx, from_html_table, load_records

    # From Excel file
    path = fetch_challenge_excel()
    source = from_xlsx(path)
    records = load_records(source, predicate=lambda r: r["role"] == "Manager")

    # From HTML table
    source = from_html_table(page, "table#dataTable")
    records = load_records(source)
"""

# Client (primary API)
from .client import RPAChallengeClient

# Backends
from .backends import Backend, PlaywrightBackend

# Data access (new API)
from .fetch import fetch_challenge_excel, fetch_challenge_excel_async
from .records import (
    EXCEL_HEADER_MAP,
    FORM_FIELD_MAP,
    HTML_TABLE_HEADER_MAP,
    RPA_CHALLENGE_SCHEMA,
    ChallengeRecord,
    from_html_table,
    from_xlsx,
    load_records,
)

# Generic data layer
from .data import (
    Column,
    DataSource,
    Schema,
    collect,
    filter_records,
    map_records,
)

# Backwards compatibility (deprecated)
from .downloads import Downloads

# Results
from .results import ResultData, Results

# Readiness
from .readiness import CheckStatus, ReadinessCheck, ReadinessResult

# Validation
from .validation import (
    DataValidationResult,
    DataValidator,
    FieldError,
    RecordValidationResult,
)

# Selectors (Page Object pattern - recommended)
from .selectors import Pages

# Selectors (legacy flat structure - deprecated, kept for backwards compatibility)
from .forms import Buttons, FormFields

# Config
from .config import RpaChallengeConfig, get_config, reset_config

# Screenshots
from .screenshots import (
    Screenshot,
    ScreenshotCapture,
    ScreenshotCollection,
    ScreenshotFormat,
)

__all__ = [
    # Client (primary API)
    "RPAChallengeClient",
    # Backends
    "Backend",
    "PlaywrightBackend",
    # Data access (new API)
    "fetch_challenge_excel",
    "fetch_challenge_excel_async",
    "from_xlsx",
    "from_html_table",
    "load_records",
    "ChallengeRecord",
    "RPA_CHALLENGE_SCHEMA",
    "EXCEL_HEADER_MAP",
    "FORM_FIELD_MAP",
    "HTML_TABLE_HEADER_MAP",
    # Generic data layer
    "DataSource",
    "Column",
    "Schema",
    "filter_records",
    "map_records",
    "collect",
    # Backwards compat (deprecated)
    "Downloads",
    # Results
    "ResultData",
    "Results",
    # Readiness
    "ReadinessCheck",
    "ReadinessResult",
    "CheckStatus",
    # Validation
    "DataValidator",
    "DataValidationResult",
    "RecordValidationResult",
    "FieldError",
    # Selectors (Page Object pattern)
    "Pages",
    # Selectors (legacy - deprecated)
    "FormFields",
    "Buttons",
    # Config
    "RpaChallengeConfig",
    "get_config",
    "reset_config",
    # Screenshots
    "Screenshot",
    "ScreenshotCapture",
    "ScreenshotCollection",
    "ScreenshotFormat",
]

__version__ = "0.2.2"
