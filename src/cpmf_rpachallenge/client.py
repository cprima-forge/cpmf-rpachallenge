"""Domain-facing client for rpachallenge.com.

The client provides a domain API independent of the backend driver.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from .downloads import ChallengeRecord, Downloads
from .validation import DataValidationResult, DataValidator

if TYPE_CHECKING:
    from .backends.protocol import Backend
    from .readiness import ReadinessResult
    from .results import ResultData


class RPAChallengeClient:
    """Domain-facing client for rpachallenge.com automation.

    Delegates to a configured backend for interaction and data access.
    The client owns the domain logic; backends handle driver-specific details.

    Usage:
        from cpmf_rpachallenge import RPAChallengeClient, PlaywrightBackend

        # With Playwright
        backend = PlaywrightBackend(page)
        client = RPAChallengeClient(backend=backend)

        # Run challenge
        records = client.get_records()
        if client.validate_records(records).is_valid:
            result = client.run(records)
            print(f"Success: {result.success_rate}%")

        # Or with async
        result = await client.run_async()
    """

    def __init__(self, backend: Backend):
        """Initialize client with a backend driver.

        Args:
            backend: Backend implementation (e.g., PlaywrightBackend).
        """
        self.backend = backend

    # -------------------------------------------------------------------------
    # Data Access (domain layer - backend independent)
    # -------------------------------------------------------------------------

    def get_records(self) -> list[ChallengeRecord]:
        """Fetch challenge data from Excel.

        Returns:
            List of 10 ChallengeRecord objects.
        """
        return Downloads.get_challenge_data()

    def validate_records(
        self,
        records: list[ChallengeRecord],
        expected_count: int | None = 10,
    ) -> DataValidationResult:
        """Validate records before automation.

        Args:
            records: List of records to validate.
            expected_count: Expected number of records.

        Returns:
            DataValidationResult with is_valid flag.
        """
        return DataValidator.validate(records, expected_count=expected_count)

    # -------------------------------------------------------------------------
    # Readiness Check (delegated to backend)
    # -------------------------------------------------------------------------

    def check_ready(self) -> ReadinessResult:
        """Check if backend is ready for automation.

        Returns:
            ReadinessResult with is_automatable flag.
        """
        return self.backend.check_ready()

    async def check_ready_async(self) -> ReadinessResult:
        """Check readiness asynchronously.

        Returns:
            ReadinessResult with is_automatable flag.
        """
        return await self.backend.check_ready_async()

    # -------------------------------------------------------------------------
    # Interaction (delegated to backend)
    # -------------------------------------------------------------------------

    def start(self) -> None:
        """Start the challenge."""
        self.backend.start()

    async def start_async(self) -> None:
        """Start the challenge asynchronously."""
        await self.backend.start_async()

    def fill_form(self, record: ChallengeRecord) -> None:
        """Fill form with record data.

        Args:
            record: ChallengeRecord with form values.
        """
        self.backend.fill_form(record)

    async def fill_form_async(self, record: ChallengeRecord) -> None:
        """Fill form asynchronously.

        Args:
            record: ChallengeRecord with form values.
        """
        await self.backend.fill_form_async(record)

    def submit(self) -> None:
        """Submit the current form."""
        self.backend.submit()

    async def submit_async(self) -> None:
        """Submit the current form asynchronously."""
        await self.backend.submit_async()

    # -------------------------------------------------------------------------
    # Results (delegated to backend)
    # -------------------------------------------------------------------------

    def get_result(self) -> ResultData:
        """Get the challenge result.

        Returns:
            ResultData with success_rate, fields_correct, time_ms.
        """
        return self.backend.get_result()

    async def get_result_async(self) -> ResultData:
        """Get result asynchronously.

        Returns:
            ResultData with success_rate, fields_correct, time_ms.
        """
        return await self.backend.get_result_async()

    def get_results(
        self,
        *,
        filter_fn: Callable[[ResultData], bool] | None = None,
    ) -> list[ResultData]:
        """Get results with optional filtering.

        Args:
            filter_fn: Optional filter function.

        Returns:
            List of ResultData matching filter.
        """
        return self.backend.get_results(filter_fn=filter_fn)

    async def get_results_async(
        self,
        *,
        filter_fn: Callable[[ResultData], bool] | None = None,
    ) -> list[ResultData]:
        """Get results asynchronously with optional filtering.

        Args:
            filter_fn: Optional filter function.

        Returns:
            List of ResultData matching filter.
        """
        return await self.backend.get_results_async(filter_fn=filter_fn)

    # -------------------------------------------------------------------------
    # Screenshots (delegated to backend, optional)
    # -------------------------------------------------------------------------

    def take_screenshot(self, label: str, full_page: bool = False) -> bytes | None:
        """Take a screenshot if backend supports it.

        Args:
            label: Label for the screenshot.
            full_page: Whether to capture full page.

        Returns:
            Screenshot bytes or None.
        """
        return self.backend.take_screenshot(label, full_page=full_page)

    async def take_screenshot_async(
        self, label: str, full_page: bool = False
    ) -> bytes | None:
        """Take screenshot asynchronously.

        Args:
            label: Label for the screenshot.
            full_page: Whether to capture full page.

        Returns:
            Screenshot bytes or None.
        """
        return await self.backend.take_screenshot_async(label, full_page=full_page)

    # -------------------------------------------------------------------------
    # High-level Operations
    # -------------------------------------------------------------------------

    def run(self, records: list[ChallengeRecord] | None = None) -> ResultData:
        """Run the complete challenge.

        Args:
            records: Records to fill. If None, fetches from Excel.

        Returns:
            ResultData with final score.
        """
        if records is None:
            records = self.get_records()

        self.start()
        for record in records:
            self.fill_form(record)
            self.submit()

        return self.get_result()

    async def run_async(
        self, records: list[ChallengeRecord] | None = None
    ) -> ResultData:
        """Run the complete challenge asynchronously.

        Args:
            records: Records to fill. If None, fetches from Excel.

        Returns:
            ResultData with final score.
        """
        if records is None:
            records = self.get_records()

        await self.start_async()
        for record in records:
            await self.fill_form_async(record)
            await self.submit_async()

        return await self.get_result_async()
