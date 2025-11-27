"""Playwright backend for rpachallenge.com automation.

Uses browser automation via Playwright for interaction and data access.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from ..domain.selectors import Pages
from ..domain.readiness import ReadinessCheck, ReadinessResult
from ..domain.results import ResultData, Results

# Backwards compatibility aliases
FormFields = Pages.ChallengePage.Fields
Buttons = Pages.ChallengePage.Buttons

if TYPE_CHECKING:
    from playwright.async_api import Page as AsyncPage
    from playwright.sync_api import Page as SyncPage

    from ..domain.records import ChallengeRecord


class PlaywrightBackend:
    """Playwright-based backend for rpachallenge.com.

    Implements the Backend protocol using browser automation.

    Usage:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("https://rpachallenge.com")

            backend = PlaywrightBackend(page)
            # Use with RPAChallengeClient
    """

    # Expose selectors for direct access if needed
    SELECTORS = {
        "first_name": FormFields.FIRST_NAME,
        "last_name": FormFields.LAST_NAME,
        "company_name": FormFields.COMPANY_NAME,
        "role": FormFields.ROLE,
        "address": FormFields.ADDRESS,
        "email": FormFields.EMAIL,
        "phone": FormFields.PHONE,
        "start_button": Buttons.START,
        "submit_button": Buttons.SUBMIT,
        "result_message": Results.MESSAGE_DETAILS,
    }

    def __init__(self, page: SyncPage | AsyncPage):
        """Initialize with a Playwright page.

        Args:
            page: Playwright Page object (sync or async).
        """
        self.page = page
        self._results_history: list[ResultData] = []

    # -------------------------------------------------------------------------
    # Interaction Layer
    # -------------------------------------------------------------------------

    def start(self) -> None:
        """Click the START button to begin the challenge."""
        self.page.click(Buttons.START)

    async def start_async(self) -> None:
        """Click the START button asynchronously."""
        await self.page.click(Buttons.START)

    def fill_form(self, record: ChallengeRecord) -> None:
        """Fill all form fields with record data.

        Args:
            record: ChallengeRecord with form data.
        """
        for field_name, value in record.as_form_data().items():
            self.page.fill(FormFields.by_name(field_name), value)

    async def fill_form_async(self, record: ChallengeRecord) -> None:
        """Fill all form fields asynchronously.

        Args:
            record: ChallengeRecord with form data.
        """
        for field_name, value in record.as_form_data().items():
            await self.page.fill(FormFields.by_name(field_name), value)

    def submit(self) -> None:
        """Click the SUBMIT button."""
        self.page.click(Buttons.SUBMIT)

    async def submit_async(self) -> None:
        """Click the SUBMIT button asynchronously."""
        await self.page.click(Buttons.SUBMIT)

    # -------------------------------------------------------------------------
    # Data Access Layer
    # -------------------------------------------------------------------------

    def check_ready(self) -> ReadinessResult:
        """Check if page is ready for automation.

        Returns:
            ReadinessResult with is_automatable flag.
        """
        return ReadinessCheck.run(self.page)

    async def check_ready_async(self) -> ReadinessResult:
        """Check if page is ready asynchronously.

        Returns:
            ReadinessResult with is_automatable flag.
        """
        return await ReadinessCheck.run_async(self.page)

    def get_result(self) -> ResultData:
        """Get and parse the result message.

        Returns:
            ResultData with success_rate, fields_correct, time_ms.
        """
        message = self.page.inner_text(Results.MESSAGE_DETAILS)
        result = Results.parse_results(message)
        self._results_history.append(result)
        return result

    async def get_result_async(self) -> ResultData:
        """Get and parse the result message asynchronously.

        Returns:
            ResultData with success_rate, fields_correct, time_ms.
        """
        message = await self.page.inner_text(Results.MESSAGE_DETAILS)
        result = Results.parse_results(message)
        self._results_history.append(result)
        return result

    def get_results(
        self,
        *,
        filter_fn: Callable[[ResultData], bool] | None = None,
    ) -> list[ResultData]:
        """Get results history with optional filtering.

        Args:
            filter_fn: Optional function to filter results.

        Returns:
            List of ResultData matching the filter.
        """
        if filter_fn is None:
            return list(self._results_history)
        return [r for r in self._results_history if filter_fn(r)]

    async def get_results_async(
        self,
        *,
        filter_fn: Callable[[ResultData], bool] | None = None,
    ) -> list[ResultData]:
        """Get results asynchronously (same as sync for Playwright).

        Args:
            filter_fn: Optional function to filter results.

        Returns:
            List of ResultData matching the filter.
        """
        return self.get_results(filter_fn=filter_fn)

    # -------------------------------------------------------------------------
    # Screenshot Support
    # -------------------------------------------------------------------------

    def take_screenshot(self, label: str, full_page: bool = False) -> bytes | None:
        """Take a screenshot of the current page.

        Args:
            label: Label for the screenshot (not used in filename here).
            full_page: Whether to capture full page.

        Returns:
            Screenshot bytes.
        """
        return self.page.screenshot(full_page=full_page)

    async def take_screenshot_async(
        self, label: str, full_page: bool = False
    ) -> bytes | None:
        """Take a screenshot asynchronously.

        Args:
            label: Label for the screenshot.
            full_page: Whether to capture full page.

        Returns:
            Screenshot bytes.
        """
        return await self.page.screenshot(full_page=full_page)
