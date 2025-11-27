"""DEPRECATED: Use fetch_challenge_excel() and from_xlsx() instead.

This module is maintained for backwards compatibility only.
All functionality has been moved to fetch.py and records.py.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import TYPE_CHECKING

from .fetch import fetch_challenge_excel
from .records import ChallengeRecord, from_xlsx, load_records

if TYPE_CHECKING:
    from .config import RpaChallengeConfig

__all__ = ["Downloads", "ChallengeRecord"]


class Downloads:
    """DEPRECATED: Use fetch_challenge_excel() and from_xlsx() instead.

    This class is maintained for backwards compatibility.
    New code should use:
        - fetch_challenge_excel() for downloading
        - from_xlsx() + load_records() for data access
    """

    # The Excel file download link (kept for reference)
    EXCEL_LINK = 'a[href*="challenge.xlsx"]'
    EXCEL_HREF = "./assets/downloadFiles/challenge.xlsx"

    @staticmethod
    def fetch_excel(
        target_dir: Path | str | None = None,
        config: RpaChallengeConfig | None = None,
    ) -> Path:
        """DEPRECATED: Use fetch_challenge_excel() instead."""
        warnings.warn(
            "Downloads.fetch_excel() is deprecated; use fetch_challenge_excel() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return fetch_challenge_excel(config=config, target_dir=target_dir)

    @staticmethod
    async def fetch_excel_async(
        target_dir: Path | str | None = None,
        config: RpaChallengeConfig | None = None,
    ) -> Path:
        """DEPRECATED: Use fetch_challenge_excel_async() instead."""
        warnings.warn(
            "Downloads.fetch_excel_async() is deprecated; use fetch_challenge_excel_async() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from .fetch import fetch_challenge_excel_async

        return await fetch_challenge_excel_async(config=config, target_dir=target_dir)

    @staticmethod
    def read_challenge_data(
        excel_path: Path | str | None = None,
        config: RpaChallengeConfig | None = None,
    ) -> list[ChallengeRecord]:
        """DEPRECATED: Use from_xlsx() + load_records() instead."""
        warnings.warn(
            "Downloads.read_challenge_data() is deprecated; use from_xlsx() + load_records() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if excel_path is None:
            excel_path = fetch_challenge_excel(config=config)
        return load_records(from_xlsx(excel_path))

    @staticmethod
    def get_challenge_data(
        config: RpaChallengeConfig | None = None,
    ) -> list[ChallengeRecord]:
        """DEPRECATED: Use fetch_challenge_excel() + from_xlsx() + load_records() instead."""
        warnings.warn(
            "Downloads.get_challenge_data() is deprecated; use fetch_challenge_excel() + from_xlsx() + load_records() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        path = fetch_challenge_excel(config=config)
        return load_records(from_xlsx(path))
