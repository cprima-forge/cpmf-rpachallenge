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
    from cpmf_rpachallenge import fetch_challenge_excel, from_xlsx, load_records

    # Procedural: download file
    path = fetch_challenge_excel()

    # Functional: create source + load
    source = from_xlsx(path)
    records = load_records(source, predicate=lambda r: r["role"] == "Manager")
"""

# Client (primary API)
from .client import RPAChallengeClient

# Backends
from .backends import Backend, PlaywrightBackend

# Data access (new API)
from .fetch import fetch_challenge_excel, fetch_challenge_excel_async
from .records import (
    FORM_FIELD_MAP,
    RPA_CHALLENGE_SCHEMA,
    ChallengeRecord,
    from_xlsx,
    load_records,
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

# Selectors (for direct access if needed)
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
    "load_records",
    "ChallengeRecord",
    "RPA_CHALLENGE_SCHEMA",
    "FORM_FIELD_MAP",
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
    # Selectors
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

__version__ = "0.2.0"
