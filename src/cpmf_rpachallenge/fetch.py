"""Procedural file acquisition - side effects live here.

DISCIPLINE: No parsing, no schema, no ChallengeRecord.
Only: config → download → return Path.
"""

import tempfile
from pathlib import Path

import httpx

from .config import RpaChallengeConfig, get_config


def fetch_challenge_excel(
    config: RpaChallengeConfig | None = None,
    target_dir: Path | str | None = None,
) -> Path:
    """Download challenge Excel file. PROCEDURAL - has side effects."""
    cfg = config or get_config()

    if target_dir is None:
        target_dir = Path(tempfile.mkdtemp(prefix="rpachallenge_"))
    else:
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / "challenge.xlsx"
    response = httpx.get(cfg.excel_url, follow_redirects=True)
    response.raise_for_status()
    target_path.write_bytes(response.content)
    return target_path


async def fetch_challenge_excel_async(
    config: RpaChallengeConfig | None = None,
    target_dir: Path | str | None = None,
) -> Path:
    """Async download. PROCEDURAL."""
    cfg = config or get_config()

    if target_dir is None:
        target_dir = Path(tempfile.mkdtemp(prefix="rpachallenge_"))
    else:
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / "challenge.xlsx"
    async with httpx.AsyncClient() as client:
        response = await client.get(cfg.excel_url, follow_redirects=True)
        response.raise_for_status()
    target_path.write_bytes(response.content)
    return target_path
