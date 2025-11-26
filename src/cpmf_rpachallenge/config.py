"""Configuration module for cpmf-rpachallenge.

Configuration hierarchy (highest to lowest priority):
1. Explicit parameters passed to functions
2. Environment variables (RPACHALLENGE_*)
3. Default values

Note: This library does NOT auto-load .env files. That is the responsibility
of the application using this library. Use python-dotenv or similar in your
application before importing this library if you need .env support.
"""

import os
from dataclasses import dataclass


def _get_env(key: str, default: str) -> str:
    """Get environment variable with default.

    Args:
        key: Environment variable name.
        default: Default value if not found.

    Returns:
        Value or default.
    """
    return os.environ.get(key, default)


def _get_env_bool(key: str, default: bool) -> bool:
    """Get boolean environment variable.

    Args:
        key: Environment variable name.
        default: Default value if not found.

    Returns:
        Boolean value.
    """
    value = os.environ.get(key)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes")


def _get_env_int(key: str, default: int) -> int:
    """Get integer environment variable.

    Args:
        key: Environment variable name.
        default: Default value if not found.

    Returns:
        Integer value.
    """
    value = os.environ.get(key)
    if value is None:
        return default
    return int(value)


def _get_env_optional(key: str) -> str | None:
    """Get optional environment variable.

    Args:
        key: Environment variable name.

    Returns:
        Value or None.
    """
    return os.environ.get(key)


@dataclass
class RpaChallengeConfig:
    """Configuration for rpachallenge.com automation.

    Attributes:
        base_url: Base URL for rpachallenge.com
        excel_url: URL to download challenge Excel file
        headless: Run browser in headless mode
        timeout_ms: Default timeout in milliseconds
        download_dir: Directory for downloaded files (None = temp dir)
        slow_mo: Slow down operations by this many milliseconds (for debugging)
    """

    base_url: str = "https://rpachallenge.com"
    excel_url: str = "https://rpachallenge.com/assets/downloadFiles/challenge.xlsx"
    headless: bool = True
    timeout_ms: int = 30000
    download_dir: str | None = None
    slow_mo: int = 0

    @classmethod
    def from_env(cls) -> "RpaChallengeConfig":
        """Load configuration from environment variables.

        Environment variables:
            RPACHALLENGE_BASE_URL: Base URL (default: https://rpachallenge.com)
            RPACHALLENGE_EXCEL_URL: Excel download URL
            RPACHALLENGE_HEADLESS: Run headless (default: true)
            RPACHALLENGE_TIMEOUT_MS: Timeout in ms (default: 30000)
            RPACHALLENGE_DOWNLOAD_DIR: Download directory (default: temp)
            RPACHALLENGE_SLOW_MO: Slow motion delay in ms (default: 0)

        Returns:
            RpaChallengeConfig instance.
        """
        return cls(
            base_url=_get_env("RPACHALLENGE_BASE_URL", cls.base_url),
            excel_url=_get_env("RPACHALLENGE_EXCEL_URL", cls.excel_url),
            headless=_get_env_bool("RPACHALLENGE_HEADLESS", cls.headless),
            timeout_ms=_get_env_int("RPACHALLENGE_TIMEOUT_MS", cls.timeout_ms),
            download_dir=_get_env_optional("RPACHALLENGE_DOWNLOAD_DIR"),
            slow_mo=_get_env_int("RPACHALLENGE_SLOW_MO", cls.slow_mo),
        )

    def with_overrides(
        self,
        base_url: str | None = None,
        excel_url: str | None = None,
        headless: bool | None = None,
        timeout_ms: int | None = None,
        download_dir: str | None = None,
        slow_mo: int | None = None,
    ) -> "RpaChallengeConfig":
        """Create a new config with overridden values.

        Args:
            base_url: Override base URL.
            excel_url: Override Excel URL.
            headless: Override headless mode.
            timeout_ms: Override timeout.
            download_dir: Override download directory.
            slow_mo: Override slow motion delay.

        Returns:
            New RpaChallengeConfig with overrides applied.
        """
        return RpaChallengeConfig(
            base_url=base_url if base_url is not None else self.base_url,
            excel_url=excel_url if excel_url is not None else self.excel_url,
            headless=headless if headless is not None else self.headless,
            timeout_ms=timeout_ms if timeout_ms is not None else self.timeout_ms,
            download_dir=download_dir if download_dir is not None else self.download_dir,
            slow_mo=slow_mo if slow_mo is not None else self.slow_mo,
        )


# Global default config instance (lazy loaded)
_default_config: RpaChallengeConfig | None = None


def get_config() -> RpaChallengeConfig:
    """Get the default configuration (lazy loaded from environment variables).

    Returns:
        Default RpaChallengeConfig instance.
    """
    global _default_config
    if _default_config is None:
        _default_config = RpaChallengeConfig.from_env()
    return _default_config


def reset_config() -> None:
    """Reset the default configuration (forces reload on next get_config())."""
    global _default_config
    _default_config = None
