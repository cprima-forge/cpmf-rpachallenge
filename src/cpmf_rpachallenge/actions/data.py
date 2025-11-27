"""Data access actions - discrete I/O operations with declared side effects.

These actions handle I/O boundaries (network, filesystem, DOM),
leaving pure transformation to the functional layer.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ._effects import side_effects

if TYPE_CHECKING:
    from playwright.async_api import Page


@side_effects("dom_read")
async def scrape_table_html(page: Page, selector: str) -> str:
    """Extract raw HTML of table element from Playwright page.

    This action performs DOM I/O - it queries the browser DOM
    to extract the HTML string of a table element.

    Args:
        page: Playwright Page object (caller owns lifecycle)
        selector: CSS selector for table element

    Returns:
        Raw HTML string of table element (inner HTML)

    Side effects:
        - dom_read: Queries DOM, waits for element

    Raises:
        playwright.async_api.TimeoutError: If table not found

    Example:
        ```python
        # Procedural approach
        html = await scrape_table_html(page, "table#dataTable")
        dicts = parse_html_table(html)
        records = [ChallengeRecord.from_dict(d) for d in dicts]

        # Functional approach
        html = await scrape_table_html(page, "table#dataTable")
        source = HtmlTableSource(html, schema, header_map)
        records = [ChallengeRecord.from_dict(d) for d in collect(source)]
        ```

    Note:
        Caller is responsible for:
        - Browser/page lifecycle (async)
        - Navigation to page (await page.goto())
        - Ensuring table is visible/loaded
    """
    table = page.locator(selector)
    await table.wait_for()
    html = await table.inner_html()
    return html


@side_effects("filesystem")
def read_excel(path: Path) -> list[dict]:
    """Read Excel file and return records as dictionaries.

    This is a convenience action that wraps XlsxSource for procedural use.

    Args:
        path: Path to .xlsx file

    Returns:
        List of dicts with keys matching RPA_CHALLENGE_SCHEMA field names.
        Uses header-based column mapping (reads first row as headers).

    Side effects:
        - filesystem: Reads file from disk

    Example:
        ```python
        # Procedural
        dicts = read_excel(Path("data.xlsx"))
        records = [ChallengeRecord.from_dict(d) for d in dicts]

        # Functional equivalent
        source = XlsxSource(Path("data.xlsx"), schema, header_map)
        records = [ChallengeRecord.from_dict(d) for d in collect(source)]
        ```

    Note:
        For functional composition, use XlsxSource directly instead.
    """
    # Import here to avoid circular dependency
    from ..domain.records import EXCEL_HEADER_MAP, RPA_CHALLENGE_SCHEMA
    from ..functional.sources.xlsx import XlsxSource

    source = XlsxSource(path, RPA_CHALLENGE_SCHEMA, header_map=EXCEL_HEADER_MAP)
    return list(source.load())


@side_effects("none")
def parse_html_table(html: str) -> list[dict]:
    """Parse HTML table string and return records as dictionaries.

    This is a convenience action (pure) that wraps HtmlTableSource for procedural use.

    Args:
        html: Raw HTML string containing a <table> element

    Returns:
        List of dicts with keys matching RPA_CHALLENGE_SCHEMA field names.
        Uses header-based column mapping (reads <th> cells).

    Side effects:
        - none (pure function)

    Example:
        ```python
        # Procedural two-step
        html = await scrape_table_html(page, "table#dataTable")
        dicts = parse_html_table(html)
        records = [ChallengeRecord.from_dict(d) for d in dicts]

        # Functional equivalent
        html = await scrape_table_html(page, "table#dataTable")
        source = HtmlTableSource(html, schema, header_map)
        records = [ChallengeRecord.from_dict(d) for d in collect(source)]
        ```

    Note:
        Expects HTML with <thead> containing <th> headers and <tbody> containing <tr> rows.
        For functional composition, use HtmlTableSource directly instead.
    """
    # Import here to avoid circular dependency
    from ..domain.records import HTML_TABLE_HEADER_MAP, RPA_CHALLENGE_SCHEMA
    from ..functional.sources.html_table import HtmlTableSource

    source = HtmlTableSource(html, RPA_CHALLENGE_SCHEMA, header_map=HTML_TABLE_HEADER_MAP)
    return list(source.load())
