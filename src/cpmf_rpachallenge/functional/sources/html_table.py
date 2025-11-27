"""Pure HTML table parser - no I/O, parses string.

Generic - no domain-specific imports.
Uses BeautifulSoup for robust HTML parsing.
"""

from typing import Any, Iterable

from bs4 import BeautifulSoup

from ..protocol import DataSource


class HtmlTableSource(DataSource[dict[str, Any]]):
    """Pure HTML table parser - accepts HTML string, no I/O.

    This source is PURE - it does not perform any I/O. It accepts an HTML string
    that has already been fetched (by an action like scrape_table_html).

    Uses header-based column mapping (reads <th> cells) to map columns by name,
    not position. This makes parsing robust to column reordering.

    Example:
        ```python
        # Step 1: Fetch HTML (action with side effects)
        html = await scrape_table_html(page, "table#dataTable")

        # Step 2: Parse HTML (pure functional)
        source = HtmlTableSource(html, schema, header_map)
        for record in source.load():
            print(record)  # {"name": "Alice", "age": 30}
        ```
    """

    def __init__(
        self,
        html: str,
        schema: list,
        header_map: dict[str, str] | None = None,
    ):
        """Initialize HTML table source.

        Args:
            html: Raw HTML string containing <table> element
            schema: Column definitions (list of Column objects)
            header_map: Optional mapping of HTML header text to schema field names
                       (e.g., {"First Name": "first_name"})

        Note:
            - Pure function (no I/O) - stores parameters only
            - Parsing happens in load() when iterated
            - Expects <thead> with <th> headers and <tbody> with <tr> rows
        """
        self.html = html
        self.schema = schema
        self.header_map = header_map

    def load(self) -> Iterable[dict[str, Any]]:
        """Parse HTML and yield records (SYNC, PURE).

        Yields:
            Dictionaries mapping column names to parsed values

        Note:
            - Uses BeautifulSoup's lxml parser for performance
            - Case-insensitive header matching (handles CSS text-transform)
            - Pads with None for missing columns
            - Skips columns not in schema
        """
        soup = BeautifulSoup(self.html, "lxml")
        table = soup.find("table")

        if not table:
            return

        # Read headers
        headers = [th.get_text(strip=True) for th in table.find_all("th")]

        # Build column index mapping
        column_indices = self._build_column_indices(headers)

        # Parse rows
        tbody = table.find("tbody")
        if not tbody:
            return

        for row in tbody.find_all("tr"):
            cells = [td.get_text(strip=True) for td in row.find_all("td")]

            record = {}
            for col in self.schema:
                if col.name in column_indices:
                    col_idx = column_indices[col.name]
                    if col_idx < len(cells):
                        record[col.name] = col.parse(cells[col_idx])
                    else:
                        record[col.name] = col.parse(None)
                else:
                    record[col.name] = col.parse(None)

            yield record

    def _build_column_indices(self, headers: list[str]) -> dict[str, int]:
        """Map schema field names to column indices.

        Args:
            headers: List of header text from <th> elements

        Returns:
            Dict mapping schema field name to column index

        Note:
            Uses case-insensitive matching to handle CSS transformations
            like text-transform: uppercase.
        """
        column_indices = {}

        if self.header_map:
            # Use provided header map
            for idx, header in enumerate(headers):
                clean_header = header.strip()
                # Case-insensitive match (CSS may transform text)
                for html_header, schema_name in self.header_map.items():
                    if clean_header.lower() == html_header.lower():
                        column_indices[schema_name] = idx
                        break
        else:
            # Fallback: direct match (schema field name == header text)
            for idx, header in enumerate(headers):
                for col in self.schema:
                    # Replace underscores and compare case-insensitive
                    if col.name.replace("_", " ").lower() == header.lower():
                        column_indices[col.name] = idx
                        break

        return column_indices
