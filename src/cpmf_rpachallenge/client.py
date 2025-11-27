"""Domain-facing client for rpachallenge.com.

⚠️ DEPRECATED - Import from procedural.client instead.

    Old (deprecated):
        from cpmf_rpachallenge.client import RPAChallengeClient

    New (recommended):
        from cpmf_rpachallenge.procedural import RPAChallengeClient

This module is kept for backwards compatibility only.
"""

import warnings

from .procedural.client import RPAChallengeClient

# Issue deprecation warning on import
warnings.warn(
    "client.py is deprecated. Use 'from cpmf_rpachallenge.procedural import RPAChallengeClient' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["RPAChallengeClient"]
