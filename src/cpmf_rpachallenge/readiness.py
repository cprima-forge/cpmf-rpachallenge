"""Readiness check module for rpachallenge.com.

Verifies that a page is ready for automation before proceeding.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .downloads import Downloads
from .forms import Buttons, FormFields

if TYPE_CHECKING:
    from playwright.async_api import Page as AsyncPage
    from playwright.sync_api import Page as SyncPage


@dataclass
class CheckStatus:
    """Status of an individual readiness check."""

    name: str
    passed: bool
    selector: str
    message: str | None = None


@dataclass
class ReadinessResult:
    """Result of a readiness check."""

    is_automatable: bool
    checks: dict[str, CheckStatus] = field(default_factory=dict)

    @property
    def failed_checks(self) -> list[str]:
        """Names of checks that failed."""
        return [name for name, status in self.checks.items() if not status.passed]

    @property
    def passed_checks(self) -> list[str]:
        """Names of checks that passed."""
        return [name for name, status in self.checks.items() if status.passed]

    @property
    def summary(self) -> str:
        """Human-readable summary of the result."""
        total = len(self.checks)
        passed = len(self.passed_checks)
        failed = len(self.failed_checks)

        if self.is_automatable:
            return f"Ready: {passed}/{total} checks passed"
        else:
            failed_names = ", ".join(self.failed_checks)
            return f"Not ready: {failed}/{total} checks failed ({failed_names})"


class ReadinessCheck:
    """Verify rpachallenge.com page is ready for automation.

    Checks for presence of required elements (Excel download link,
    Start button, form fields) before automation begins.

    Usage (async):
        result = await ReadinessCheck.run_async(page)
        if result.is_automatable:
            # proceed with automation
        else:
            print(result.summary)

    Usage (sync):
        result = ReadinessCheck.run(page)
        if not result.is_automatable:
            raise RuntimeError(result.summary)
    """

    # Default checks to perform (uses existing selectors)
    CHECKS: dict[str, str] = {
        "excel_link": Downloads.EXCEL_LINK,
        "start_button": Buttons.START,
        "first_name": FormFields.FIRST_NAME,
        "last_name": FormFields.LAST_NAME,
        "email": FormFields.EMAIL,
        "phone": FormFields.PHONE,
        "address": FormFields.ADDRESS,
        "company_name": FormFields.COMPANY_NAME,
        "role": FormFields.ROLE,
    }

    @classmethod
    def run(
        cls,
        page: SyncPage,
        checks: list[str] | None = None,
    ) -> ReadinessResult:
        """Run readiness checks synchronously.

        Args:
            page: Playwright sync Page object.
            checks: List of check names to run. If None, runs all checks.

        Returns:
            ReadinessResult with is_automatable bool and individual check results.
        """
        check_names = checks or list(cls.CHECKS.keys())
        results: dict[str, CheckStatus] = {}

        for name in check_names:
            if name not in cls.CHECKS:
                results[name] = CheckStatus(
                    name=name,
                    passed=False,
                    selector="",
                    message=f"Unknown check: {name}",
                )
                continue

            selector = cls.CHECKS[name]
            try:
                element = page.query_selector(selector)
                results[name] = CheckStatus(
                    name=name,
                    passed=element is not None,
                    selector=selector,
                    message=None if element else f"Element not found: {selector}",
                )
            except Exception as e:
                results[name] = CheckStatus(
                    name=name,
                    passed=False,
                    selector=selector,
                    message=f"Error checking {selector}: {e}",
                )

        return ReadinessResult(
            is_automatable=all(status.passed for status in results.values()),
            checks=results,
        )

    @classmethod
    async def run_async(
        cls,
        page: AsyncPage,
        checks: list[str] | None = None,
    ) -> ReadinessResult:
        """Run readiness checks asynchronously.

        Args:
            page: Playwright async Page object.
            checks: List of check names to run. If None, runs all checks.

        Returns:
            ReadinessResult with is_automatable bool and individual check results.
        """
        check_names = checks or list(cls.CHECKS.keys())
        results: dict[str, CheckStatus] = {}

        for name in check_names:
            if name not in cls.CHECKS:
                results[name] = CheckStatus(
                    name=name,
                    passed=False,
                    selector="",
                    message=f"Unknown check: {name}",
                )
                continue

            selector = cls.CHECKS[name]
            try:
                element = await page.query_selector(selector)
                results[name] = CheckStatus(
                    name=name,
                    passed=element is not None,
                    selector=selector,
                    message=None if element else f"Element not found: {selector}",
                )
            except Exception as e:
                results[name] = CheckStatus(
                    name=name,
                    passed=False,
                    selector=selector,
                    message=f"Error checking {selector}: {e}",
                )

        return ReadinessResult(
            is_automatable=all(status.passed for status in results.values()),
            checks=results,
        )
