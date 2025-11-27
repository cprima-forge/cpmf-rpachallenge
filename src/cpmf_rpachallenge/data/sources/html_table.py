"""Generic HTML table source - schema-driven scraping.

Generic - no domain-specific imports.
Playwright dependency isolated to this module only.
"""

from typing import Any, AsyncIterable

from playwright.async_api import Page

from ..protocol import DataSource
from ..schema import Schema


class HtmlTableSource(DataSource[dict[str, Any]]):
    """Generic HTML table scraper - schema-driven normalization.

    Treats DOM as raw material that gets normalized to schema:
    - Schema defines column names + types (authoritative)
    - DOM provides cell text values (raw material)
    - **Header-based mapping**: Reads <th> headers and maps by column name
    - Mismatch handling: pad with None (fewer cells) or truncate (more cells)

    Non-paginated only - reads entire table in one pass.
    Uses async Playwright API to match codebase pattern.

    Example:
        schema = [
            Column("name", str),
            Column("age", int),
        ]
        source = HtmlTableSource(
            page,
            table_selector="table#users",
            schema=schema,
        )
        async for record in source.load():
            print(record)  # {"name": "Alice", "age": 30}
    """

    def __init__(
        self,
        page: Page,
        *,
        table_selector: str,
        row_selector: str = "tbody tr",
        header_selector: str = "thead tr th",
        schema: Schema,
        header_map: dict[str, str] | None = None,
    ) -> None:
        """Initialize HTML table source.

        Args:
            page: Async Playwright Page object (caller owns browser lifecycle)
            table_selector: CSS selector for table root element
            row_selector: CSS selector for data rows (default: "tbody tr")
            header_selector: CSS selector for header cells (default: "thead tr th")
            schema: Column definitions (names, types, parsers)
            header_map: Optional mapping of HTML header text to schema field names
                       (e.g., {"First Name": "first_name"})

        Note:
            The caller is responsible for:
            - Browser/context/page lifecycle (async)
            - Navigation to page (await page.goto())
            - Ensuring table is visible/loaded
        """
        self._page = page
        self._table_selector = table_selector
        self._row_selector = row_selector
        self._header_selector = header_selector
        self._schema = schema
        self._header_map = header_map
        self._column_indices: dict[str, int] | None = None

    async def _build_column_indices(self) -> dict[str, int]:
        """Build mapping of schema field names to column indices.

        Reads <th> headers from the table and maps them to schema field names
        using the header_map (if provided).

        Returns:
            Dict mapping schema field name to column index
        """
        # Locate header cells
        table = self._page.locator(self._table_selector)
        headers = table.locator(self._header_selector)
        header_count = await headers.count()

        # Read header text values
        header_texts = []
        for i in range(header_count):
            text = await headers.nth(i).inner_text()
            header_texts.append(text.strip())

        # Build mapping: schema_field_name -> column_index
        column_indices = {}
        for col in self._schema:
            schema_name = col.name
            # If header_map provided, use it to find HTML header text
            if self._header_map and schema_name in self._header_map.values():
                # Find the HTML header that maps to this schema field
                html_header = next(
                    (k for k, v in self._header_map.items() if v == schema_name),
                    None
                )
                if html_header and html_header in header_texts:
                    column_indices[schema_name] = header_texts.index(html_header)
            else:
                # Try direct match (schema field name == header text, case-insensitive)
                matching_headers = [
                    (idx, h) for idx, h in enumerate(header_texts)
                    if h.lower() == schema_name.lower().replace("_", " ")
                ]
                if matching_headers:
                    column_indices[schema_name] = matching_headers[0][0]

        return column_indices

    async def load(self) -> AsyncIterable[dict[str, Any]]:
        """Yield records from HTML table asynchronously.

        Waits for table, then scrapes all rows.
        **Reads header row** to map columns by name (not position).
        Normalizes cell count to schema length (pad/truncate).
        Parses each cell via Column.parse().

        Yields:
            Dict mapping column names to parsed values

        Raises:
            TimeoutError: If table not found or not visible
            ValueError: If Column.parse() fails (propagated from schema)
        """
        # Wait for table to be present
        table = self._page.locator(self._table_selector)
        await table.wait_for()

        # Build column index mapping from headers (once)
        if self._column_indices is None:
            self._column_indices = await self._build_column_indices()

        # Get all data rows
        rows = table.locator(self._row_selector)
        row_count = await rows.count()

        # Process each row
        for i in range(row_count):
            row = rows.nth(i)
            cells = row.locator("td")
            cell_count = await cells.count()

            # Read all cell values into a list
            all_cell_values: list[str] = []
            for j in range(cell_count):
                text = await cells.nth(j).inner_text()
                all_cell_values.append(text.strip())

            # Map cells to schema fields using column indices
            record = {}
            for col in self._schema:
                if col.name in self._column_indices:
                    col_idx = self._column_indices[col.name]
                    if col_idx < len(all_cell_values):
                        record[col.name] = col.parse(all_cell_values[col_idx])
                    else:
                        record[col.name] = col.parse(None)
                else:
                    # Column not found in headers, use None
                    record[col.name] = col.parse(None)

            yield record
