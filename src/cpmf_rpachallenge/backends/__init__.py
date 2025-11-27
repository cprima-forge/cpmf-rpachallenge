"""Backend implementations for RPAChallengeClient."""

from .protocol import Backend
from .playwright import PlaywrightBackend

__all__ = [
    "Backend",
    "PlaywrightBackend",
]
