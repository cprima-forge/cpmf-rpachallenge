"""Selectors and utilities for rpachallenge.com automation."""

from .forms import FormFields, Buttons
from .downloads import Downloads, ChallengeRecord
from .results import Results, ResultData
from .config import RpaChallengeConfig, get_config, reset_config
from .readiness import ReadinessCheck, ReadinessResult, CheckStatus
from .screenshots import (
    Screenshot,
    ScreenshotCapture,
    ScreenshotCollection,
    ScreenshotFormat,
)
from .validation import (
    DataValidator,
    DataValidationResult,
    RecordValidationResult,
    FieldError,
)

__all__ = [
    # Selectors
    "FormFields",
    "Buttons",
    # Downloads
    "Downloads",
    "ChallengeRecord",
    # Results
    "Results",
    "ResultData",
    # Config
    "RpaChallengeConfig",
    "get_config",
    "reset_config",
    # Readiness
    "ReadinessCheck",
    "ReadinessResult",
    "CheckStatus",
    # Screenshots
    "Screenshot",
    "ScreenshotCapture",
    "ScreenshotCollection",
    "ScreenshotFormat",
    # Validation
    "DataValidator",
    "DataValidationResult",
    "RecordValidationResult",
    "FieldError",
]

__version__ = "0.1.1"
