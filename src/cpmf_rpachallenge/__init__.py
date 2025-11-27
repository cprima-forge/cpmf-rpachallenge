"""Domain SDK for rpachallenge.com automation.

Architecture (New Structure):
    - procedural/: Imperative, step-by-step workflows (RPAChallengeClient)
    - functional/: Pure transformations, composable data sources
    - actions/: Discrete I/O operations with declared side effects
    - domain/: Business logic, schemas, validation, results, selectors
    - backends/: Driver implementations (Playwright, API)

Quick Start (Recommended API):
    from cpmf_rpachallenge.procedural import RPAChallengeClient
    from cpmf_rpachallenge.backends import PlaywrightBackend
    from cpmf_rpachallenge.domain import ChallengeRecord, from_xlsx, load_records
    from cpmf_rpachallenge.domain.selectors import Pages

    backend = PlaywrightBackend(page)
    client = RPAChallengeClient(backend=backend)
    result = client.run()

Functional Data Access (Pure, Composable):
    from cpmf_rpachallenge import fetch_challenge_excel
    from cpmf_rpachallenge.domain import from_xlsx, load_records
    from cpmf_rpachallenge.functional import filter_records
    from cpmf_rpachallenge.actions import scrape_table_html, parse_html_table

    # From Excel
    path = fetch_challenge_excel()
    source = from_xlsx(path)
    records = load_records(source, predicate=lambda r: r["role"] == "Manager")

    # From HTML table (two-step: scrape + parse)
    html = await scrape_table_html(page, "table#dataTable")  # I/O action
    dicts = parse_html_table(html)  # Pure transformation
    records = [ChallengeRecord.from_dict(d) for d in dicts]

Backwards Compatibility:
    All legacy imports still work but issue DeprecationWarnings.
    Old imports redirect to new locations for gradual migration.
"""

# ===== PRIMARY MODERN API (RECOMMENDED) =====

# Procedural layer - High-level client
from .procedural import RPAChallengeClient

# Backends
from .backends import Backend, PlaywrightBackend

# Domain layer - Records, validation, results, selectors
from .domain import (
    # Records and schemas
    ChallengeRecord,
    EXCEL_HEADER_MAP,
    FORM_FIELD_MAP,
    HTML_TABLE_HEADER_MAP,
    RPA_CHALLENGE_SCHEMA,
    from_xlsx,
    load_records,
    # Validation
    DataValidationResult,
    DataValidator,
    FieldError,
    RecordValidationResult,
    # Results
    ResultData,
    Results,
    # Readiness
    ReadinessCheck,
    ReadinessResult,
    # Selectors (Page Object pattern)
    Pages,
)

# Functional layer - Pure data sources and combinators
from .functional import (
    Column,
    DataSource,
    Schema,
    collect,
    filter_records,
    map_records,
    HtmlTableSource,
    XlsxSource,
)

# Actions layer - I/O operations with side effects
from .actions import parse_html_table, read_excel, scrape_table_html, side_effects

# Data fetching
from .fetch import fetch_challenge_excel, fetch_challenge_excel_async

# Config
from .config import RpaChallengeConfig, get_config, reset_config

# Readiness (CheckStatus enum)
from .domain.readiness import CheckStatus

# Screenshots
from .screenshots import (
    Screenshot,
    ScreenshotCapture,
    ScreenshotCollection,
    ScreenshotFormat,
)

# ===== BACKWARDS COMPATIBILITY (DEPRECATED) =====

# These imports still work but issue DeprecationWarnings
from .downloads import Downloads  # Use fetch_challenge_excel() instead
from .forms import Buttons, FormFields  # Use Pages.ChallengePage.* instead

# Note: Importing from .client, .records, .validation directly will trigger warnings
# Use .procedural, .domain imports instead

__all__ = [
    # ===== Modern API (Recommended) =====
    # Procedural layer
    "RPAChallengeClient",
    # Backends
    "Backend",
    "PlaywrightBackend",
    # Domain - Records
    "ChallengeRecord",
    "RPA_CHALLENGE_SCHEMA",
    "EXCEL_HEADER_MAP",
    "FORM_FIELD_MAP",
    "HTML_TABLE_HEADER_MAP",
    "from_xlsx",
    "load_records",
    # Domain - Validation
    "DataValidator",
    "DataValidationResult",
    "RecordValidationResult",
    "FieldError",
    # Domain - Results
    "ResultData",
    "Results",
    # Domain - Readiness
    "ReadinessCheck",
    "ReadinessResult",
    "CheckStatus",
    # Domain - Selectors
    "Pages",
    # Functional layer
    "DataSource",
    "Column",
    "Schema",
    "filter_records",
    "map_records",
    "collect",
    "HtmlTableSource",
    "XlsxSource",
    # Actions layer
    "scrape_table_html",
    "read_excel",
    "parse_html_table",
    "side_effects",
    # Data fetching
    "fetch_challenge_excel",
    "fetch_challenge_excel_async",
    # Config
    "RpaChallengeConfig",
    "get_config",
    "reset_config",
    # Screenshots
    "Screenshot",
    "ScreenshotCapture",
    "ScreenshotCollection",
    "ScreenshotFormat",
    # ===== Backwards Compatibility (Deprecated) =====
    "Downloads",  # DEPRECATED
    "FormFields",  # DEPRECATED - use Pages.ChallengePage.Fields
    "Buttons",  # DEPRECATED - use Pages.ChallengePage.Buttons
]

__version__ = "0.3.1"
