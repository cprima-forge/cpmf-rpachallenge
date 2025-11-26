"""Screenshot capture and montage utilities for rpachallenge.com automation.

Provides screenshot capture during automation with support for:
- PNG, JPEG, and PDF formats
- Full page or viewport screenshots
- Montage/grid creation from multiple screenshots
- Both sync and async Playwright APIs
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import Page as AsyncPage
    from playwright.sync_api import Page as SyncPage


class ScreenshotFormat(str, Enum):
    """Supported screenshot formats."""

    PNG = "png"
    JPEG = "jpeg"
    PDF = "pdf"


@dataclass
class Screenshot:
    """A captured screenshot with metadata."""

    data: bytes
    format: ScreenshotFormat
    label: str
    index: int
    full_page: bool = False

    def save(self, path: str | Path) -> Path:
        """Save screenshot to file.

        Args:
            path: Destination file path.

        Returns:
            Path to the saved file.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.data)
        return path

    def to_pil_image(self):
        """Convert screenshot to PIL Image.

        Returns:
            PIL.Image.Image object.

        Raises:
            ValueError: If format is PDF (not convertible to PIL Image).
            ImportError: If Pillow is not installed.
        """
        if self.format == ScreenshotFormat.PDF:
            raise ValueError("PDF screenshots cannot be converted to PIL Image")

        from PIL import Image

        return Image.open(io.BytesIO(self.data))


@dataclass
class ScreenshotCollection:
    """Collection of screenshots with montage capabilities."""

    screenshots: list[Screenshot] = field(default_factory=list)

    def add(self, screenshot: Screenshot) -> None:
        """Add a screenshot to the collection."""
        self.screenshots.append(screenshot)

    def __len__(self) -> int:
        return len(self.screenshots)

    def __iter__(self):
        return iter(self.screenshots)

    def __getitem__(self, index: int) -> Screenshot:
        return self.screenshots[index]

    def get_by_label(self, label: str) -> list[Screenshot]:
        """Get all screenshots with a specific label."""
        return [s for s in self.screenshots if s.label == label]

    def save_all(self, directory: str | Path, prefix: str = "screenshot") -> list[Path]:
        """Save all screenshots to a directory.

        Args:
            directory: Target directory.
            prefix: Filename prefix.

        Returns:
            List of saved file paths.
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        paths = []
        for screenshot in self.screenshots:
            ext = screenshot.format.value
            filename = f"{prefix}_{screenshot.index:03d}_{screenshot.label}.{ext}"
            path = directory / filename
            screenshot.save(path)
            paths.append(path)

        return paths

    def create_montage(
        self,
        columns: int | None = None,
        padding: int = 10,
        background_color: tuple[int, int, int] = (255, 255, 255),
        labels: list[str] | None = None,
    ) -> bytes:
        """Create a montage/grid from all PNG/JPEG screenshots.

        Args:
            columns: Number of columns in grid. If None, creates a single row.
            padding: Padding between images in pixels.
            background_color: RGB background color tuple.
            labels: If provided, only include screenshots with these labels.

        Returns:
            PNG image data as bytes.

        Raises:
            ValueError: If no compatible screenshots available.
            ImportError: If Pillow is not installed.
        """
        from PIL import Image

        # Filter to image-compatible screenshots
        image_screenshots = [
            s for s in self.screenshots if s.format != ScreenshotFormat.PDF
        ]

        if labels:
            image_screenshots = [s for s in image_screenshots if s.label in labels]

        if not image_screenshots:
            raise ValueError("No PNG/JPEG screenshots available for montage")

        # Convert to PIL images
        images = [s.to_pil_image() for s in image_screenshots]

        # Calculate grid dimensions
        n_images = len(images)
        if columns is None:
            columns = n_images  # Single row
        rows = (n_images + columns - 1) // columns

        # Find max dimensions for uniform grid
        max_width = max(img.width for img in images)
        max_height = max(img.height for img in images)

        # Calculate canvas size
        canvas_width = columns * max_width + (columns + 1) * padding
        canvas_height = rows * max_height + (rows + 1) * padding

        # Create canvas
        canvas = Image.new("RGB", (canvas_width, canvas_height), background_color)

        # Paste images
        for i, img in enumerate(images):
            row = i // columns
            col = i % columns
            x = padding + col * (max_width + padding)
            y = padding + row * (max_height + padding)
            # Center image in cell if smaller than max
            x_offset = (max_width - img.width) // 2
            y_offset = (max_height - img.height) // 2
            canvas.paste(img, (x + x_offset, y + y_offset))

        # Convert to bytes
        buffer = io.BytesIO()
        canvas.save(buffer, format="PNG")
        return buffer.getvalue()

    def create_vertical_strip(
        self,
        padding: int = 10,
        background_color: tuple[int, int, int] = (255, 255, 255),
        labels: list[str] | None = None,
    ) -> bytes:
        """Create a vertical strip of all screenshots.

        Args:
            padding: Padding between images in pixels.
            background_color: RGB background color tuple.
            labels: If provided, only include screenshots with these labels.

        Returns:
            PNG image data as bytes.
        """
        return self.create_montage(
            columns=1,
            padding=padding,
            background_color=background_color,
            labels=labels,
        )

    def create_horizontal_strip(
        self,
        padding: int = 10,
        background_color: tuple[int, int, int] = (255, 255, 255),
        labels: list[str] | None = None,
    ) -> bytes:
        """Create a horizontal strip of all screenshots.

        Args:
            padding: Padding between images in pixels.
            background_color: RGB background color tuple.
            labels: If provided, only include screenshots with these labels.

        Returns:
            PNG image data as bytes.
        """
        return self.create_montage(
            columns=None,  # All in one row
            padding=padding,
            background_color=background_color,
            labels=labels,
        )


class ScreenshotCapture:
    """Capture screenshots during rpachallenge.com automation.

    Usage (async):
        capture = ScreenshotCapture()
        await capture.take_async(page, label="before_submit")
        await capture.take_async(page, label="result", full_page=True)

        # Save all
        capture.collection.save_all("./screenshots")

        # Create montage
        montage = capture.collection.create_montage(columns=2)
        Path("montage.png").write_bytes(montage)

    Usage (sync):
        capture = ScreenshotCapture()
        capture.take(page, label="form_filled")
        capture.take_pdf(page, label="result")
    """

    def __init__(
        self,
        default_format: ScreenshotFormat = ScreenshotFormat.PNG,
        default_full_page: bool = False,
        jpeg_quality: int = 80,
    ):
        """Initialize screenshot capture.

        Args:
            default_format: Default format for screenshots.
            default_full_page: Whether to capture full page by default.
            jpeg_quality: Quality for JPEG screenshots (0-100).
        """
        self.default_format = default_format
        self.default_full_page = default_full_page
        self.jpeg_quality = jpeg_quality
        self.collection = ScreenshotCollection()
        self._index = 0

    def _next_index(self) -> int:
        """Get next screenshot index."""
        idx = self._index
        self._index += 1
        return idx

    def take(
        self,
        page: SyncPage,
        label: str = "screenshot",
        format: ScreenshotFormat | None = None,
        full_page: bool | None = None,
    ) -> Screenshot:
        """Take a screenshot synchronously.

        Args:
            page: Playwright sync Page object.
            label: Label for the screenshot (e.g., "before_submit", "result").
            format: Screenshot format. If None, uses default_format.
            full_page: Capture full scrollable page. If None, uses default_full_page.

        Returns:
            Screenshot object.
        """
        fmt = format or self.default_format
        fp = full_page if full_page is not None else self.default_full_page

        if fmt == ScreenshotFormat.PDF:
            data = page.pdf()
        elif fmt == ScreenshotFormat.JPEG:
            data = page.screenshot(type="jpeg", quality=self.jpeg_quality, full_page=fp)
        else:
            data = page.screenshot(type="png", full_page=fp)

        screenshot = Screenshot(
            data=data,
            format=fmt,
            label=label,
            index=self._next_index(),
            full_page=fp,
        )
        self.collection.add(screenshot)
        return screenshot

    async def take_async(
        self,
        page: AsyncPage,
        label: str = "screenshot",
        format: ScreenshotFormat | None = None,
        full_page: bool | None = None,
    ) -> Screenshot:
        """Take a screenshot asynchronously.

        Args:
            page: Playwright async Page object.
            label: Label for the screenshot (e.g., "before_submit", "result").
            format: Screenshot format. If None, uses default_format.
            full_page: Capture full scrollable page. If None, uses default_full_page.

        Returns:
            Screenshot object.
        """
        fmt = format or self.default_format
        fp = full_page if full_page is not None else self.default_full_page

        if fmt == ScreenshotFormat.PDF:
            data = await page.pdf()
        elif fmt == ScreenshotFormat.JPEG:
            data = await page.screenshot(
                type="jpeg", quality=self.jpeg_quality, full_page=fp
            )
        else:
            data = await page.screenshot(type="png", full_page=fp)

        screenshot = Screenshot(
            data=data,
            format=fmt,
            label=label,
            index=self._next_index(),
            full_page=fp,
        )
        self.collection.add(screenshot)
        return screenshot

    def take_pdf(
        self,
        page: SyncPage,
        label: str = "screenshot",
    ) -> Screenshot:
        """Take a PDF screenshot synchronously (Chromium only).

        Args:
            page: Playwright sync Page object.
            label: Label for the screenshot.

        Returns:
            Screenshot object.
        """
        return self.take(page, label=label, format=ScreenshotFormat.PDF)

    async def take_pdf_async(
        self,
        page: AsyncPage,
        label: str = "screenshot",
    ) -> Screenshot:
        """Take a PDF screenshot asynchronously (Chromium only).

        Args:
            page: Playwright async Page object.
            label: Label for the screenshot.

        Returns:
            Screenshot object.
        """
        return await self.take_async(page, label=label, format=ScreenshotFormat.PDF)

    def reset(self) -> None:
        """Reset the capture state, clearing all screenshots."""
        self.collection = ScreenshotCollection()
        self._index = 0
