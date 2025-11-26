"""Download utilities for rpachallenge.com"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
import openpyxl

if TYPE_CHECKING:
    from .config import RpaChallengeConfig


@dataclass
class ChallengeRecord:
    """A single record from the challenge Excel file."""

    first_name: str
    last_name: str
    company_name: str
    role: str
    address: str
    email: str
    phone: str

    def as_form_data(self) -> dict[str, str]:
        """Return data mapped to form field names (ng-reflect-name values)."""
        return {
            "labelFirstName": self.first_name,
            "labelLastName": self.last_name,
            "labelCompanyName": self.company_name,
            "labelRole": self.role,
            "labelAddress": self.address,
            "labelEmail": self.email,
            "labelPhone": self.phone,
        }


class Downloads:
    """Download link selectors and utilities."""

    # The Excel file download link
    EXCEL_LINK = 'a[href*="challenge.xlsx"]'
    EXCEL_HREF = "./assets/downloadFiles/challenge.xlsx"

    @staticmethod
    def _get_excel_url(config: RpaChallengeConfig | None = None) -> str:
        """Get Excel URL from config or default."""
        if config is not None:
            return config.excel_url
        from .config import get_config
        return get_config().excel_url

    @staticmethod
    def _get_download_dir(config: RpaChallengeConfig | None = None) -> Path | None:
        """Get download directory from config or default."""
        if config is not None:
            return Path(config.download_dir) if config.download_dir else None
        from .config import get_config
        cfg = get_config()
        return Path(cfg.download_dir) if cfg.download_dir else None

    @staticmethod
    def fetch_excel(
        target_dir: Path | str | None = None,
        config: RpaChallengeConfig | None = None,
    ) -> Path:
        """Fetch the challenge Excel file to a local directory.

        Args:
            target_dir: Directory to save the file. If None, uses config or temp directory.
            config: Configuration object. If None, uses global config.

        Returns:
            Path to the downloaded challenge.xlsx file.
        """
        # Resolve target directory
        if target_dir is None:
            target_dir = Downloads._get_download_dir(config)
        if target_dir is None:
            target_dir = Path(tempfile.mkdtemp(prefix="rpachallenge_"))
        else:
            target_dir = Path(target_dir)
            target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / "challenge.xlsx"

        excel_url = Downloads._get_excel_url(config)
        response = httpx.get(excel_url, follow_redirects=True)
        response.raise_for_status()

        target_path.write_bytes(response.content)

        return target_path

    @staticmethod
    async def fetch_excel_async(
        target_dir: Path | str | None = None,
        config: RpaChallengeConfig | None = None,
    ) -> Path:
        """Fetch the challenge Excel file asynchronously.

        Args:
            target_dir: Directory to save the file. If None, uses config or temp directory.
            config: Configuration object. If None, uses global config.

        Returns:
            Path to the downloaded challenge.xlsx file.
        """
        # Resolve target directory
        if target_dir is None:
            target_dir = Downloads._get_download_dir(config)
        if target_dir is None:
            target_dir = Path(tempfile.mkdtemp(prefix="rpachallenge_"))
        else:
            target_dir = Path(target_dir)
            target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / "challenge.xlsx"

        excel_url = Downloads._get_excel_url(config)
        async with httpx.AsyncClient() as client:
            response = await client.get(excel_url, follow_redirects=True)
            response.raise_for_status()

        target_path.write_bytes(response.content)

        return target_path

    @staticmethod
    def read_challenge_data(
        excel_path: Path | str | None = None,
        config: RpaChallengeConfig | None = None,
    ) -> list[ChallengeRecord]:
        """Read the challenge Excel file and return structured records.

        Args:
            excel_path: Path to the Excel file. If None, fetches from web.
            config: Configuration object. If None, uses global config.

        Returns:
            List of 10 ChallengeRecord objects ready for form filling.
        """
        if excel_path is None:
            excel_path = Downloads.fetch_excel(config=config)

        wb = openpyxl.load_workbook(excel_path)
        sheet = wb.active

        records = []
        for row in sheet.iter_rows(min_row=2, max_row=11, values_only=True):
            # Skip empty rows
            if row[0] is None:
                continue

            records.append(
                ChallengeRecord(
                    first_name=str(row[0]),
                    last_name=str(row[1]),
                    company_name=str(row[2]),
                    role=str(row[3]),
                    address=str(row[4]),
                    email=str(row[5]),
                    phone=str(row[6]),  # Convert int to string for form input
                )
            )

        return records

    @staticmethod
    def get_challenge_data(config: RpaChallengeConfig | None = None) -> list[ChallengeRecord]:
        """Convenience method: fetch Excel and return records in one call.

        Args:
            config: Configuration object. If None, uses global config.

        Returns:
            List of 10 ChallengeRecord objects ready for form filling.
        """
        return Downloads.read_challenge_data(config=config)
