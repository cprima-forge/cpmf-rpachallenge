"""Backend protocol defining the driver interface.

All backends must implement this protocol to be used with RPAChallengeClient.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Protocol, runtime_checkable

if TYPE_CHECKING:
    from ..downloads import ChallengeRecord
    from ..readiness import ReadinessResult
    from ..results import ResultData


@runtime_checkable
class Backend(Protocol):
    """Protocol for rpachallenge.com backend drivers.

    Backends handle the interaction layer (clicks, typing, navigation)
    and data access layer (fetching results, parsing tables).

    Implementations:
        - PlaywrightBackend: Browser automation via Playwright
        - ApiBackend: Direct HTTP/REST (if available)
        - MixedBackend: API when possible, UI when needed
    """

    # -------------------------------------------------------------------------
    # Interaction Layer
    # -------------------------------------------------------------------------

    def start(self) -> None:
        """Start the challenge (click START button or equivalent)."""
        ...

    async def start_async(self) -> None:
        """Start the challenge asynchronously."""
        ...

    def fill_form(self, record: ChallengeRecord) -> None:
        """Fill form fields with record data.

        Args:
            record: ChallengeRecord containing form field values.
        """
        ...

    async def fill_form_async(self, record: ChallengeRecord) -> None:
        """Fill form fields asynchronously."""
        ...

    def submit(self) -> None:
        """Submit the current form."""
        ...

    async def submit_async(self) -> None:
        """Submit the current form asynchronously."""
        ...

    # -------------------------------------------------------------------------
    # Data Access Layer
    # -------------------------------------------------------------------------

    def check_ready(self) -> ReadinessResult:
        """Check if the page/API is ready for automation.

        Returns:
            ReadinessResult with is_automatable flag and check details.
        """
        ...

    async def check_ready_async(self) -> ReadinessResult:
        """Check readiness asynchronously."""
        ...

    def get_result(self) -> ResultData:
        """Get the challenge result after completion.

        Returns:
            ResultData with success_rate, fields_correct, time_ms.
        """
        ...

    async def get_result_async(self) -> ResultData:
        """Get result asynchronously."""
        ...

    def get_results(
        self,
        *,
        filter_fn: Callable[[ResultData], bool] | None = None,
    ) -> list[ResultData]:
        """Get results with optional filtering.

        Args:
            filter_fn: Optional function to filter results.

        Returns:
            List of ResultData matching the filter.
        """
        ...

    async def get_results_async(
        self,
        *,
        filter_fn: Callable[[ResultData], bool] | None = None,
    ) -> list[ResultData]:
        """Get results asynchronously with optional filtering."""
        ...

    # -------------------------------------------------------------------------
    # Screenshot Support (optional)
    # -------------------------------------------------------------------------

    def take_screenshot(self, label: str, full_page: bool = False) -> bytes | None:
        """Take a screenshot if supported by backend.

        Args:
            label: Label for the screenshot.
            full_page: Whether to capture full page.

        Returns:
            Screenshot bytes or None if not supported.
        """
        ...

    async def take_screenshot_async(
        self, label: str, full_page: bool = False
    ) -> bytes | None:
        """Take screenshot asynchronously."""
        ...
