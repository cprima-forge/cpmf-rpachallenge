"""RPAChallenge domain: schema, record type, and factory functions."""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from playwright.async_api import Page

from .data.protocol import DataSource
from .data.schema import Column, Schema
from .data.sources.xlsx import XlsxSource

# RPAChallenge schema with explicit types
# NOTE: Order doesn't matter since we map by column name from Excel headers
RPA_CHALLENGE_SCHEMA: Schema = [
    Column("first_name", str),
    Column("last_name", str),
    Column("company_name", str),
    Column("role", str),
    Column("address", str),
    Column("email", str),
    Column("phone", str),  # str not int - form input needs string
]

# Form field mapping (ng-reflect-name values)
FORM_FIELD_MAP = {
    "first_name": "labelFirstName",
    "last_name": "labelLastName",
    "company_name": "labelCompanyName",
    "role": "labelRole",
    "address": "labelAddress",
    "email": "labelEmail",
    "phone": "labelPhone",
}

# Excel header mapping (Excel column name -> schema field name)
# Used by XlsxSource for header-based column mapping
EXCEL_HEADER_MAP = {
    "First Name": "first_name",
    "Last Name": "last_name",
    "Phone Number": "phone",
    "Email": "email",
    "Address": "address",
    "Company Name": "company_name",
    "Role in Company": "role",
}

# HTML table header mapping (th text -> schema field name)
# Used by HtmlTableSource for header-based column mapping
HTML_TABLE_HEADER_MAP = {
    "First Name": "first_name",
    "Last Name": "last_name",
    "Phone Number": "phone",
    "Email": "email",
    "Address": "address",
    "Company Name": "company_name",
    "Role in Company": "role",
}


@dataclass
class ChallengeRecord:
    """Typed record for rpachallenge.com.

    NOTE: Field order doesn't matter since mapping is by column name from Excel headers.
    """

    first_name: str
    last_name: str
    company_name: str
    role: str
    address: str
    email: str
    phone: str

    @classmethod
    def from_dict(cls, data: dict) -> "ChallengeRecord":
        """Create record from dictionary."""
        return cls(**{col.name: data[col.name] for col in RPA_CHALLENGE_SCHEMA})

    def as_form_data(self) -> dict[str, str]:
        """Map to form field names."""
        return {FORM_FIELD_MAP[k]: getattr(self, k) for k in FORM_FIELD_MAP}


# Factory functions - keep sources generic

def from_xlsx(path: Path | str) -> DataSource[dict]:
    """Create data source from Excel file path.

    Uses header-based column mapping to map Excel column names
    (e.g., "First Name") to schema field names (e.g., "first_name").

    Args:
        path: Path to Excel file (.xlsx)

    Returns:
        DataSource yielding dicts matching RPA_CHALLENGE_SCHEMA

    Example:
        source = from_xlsx("challenge.xlsx")
        records = load_records(source)
    """
    return XlsxSource(path, RPA_CHALLENGE_SCHEMA, header_map=EXCEL_HEADER_MAP)


def from_html_table(
    page: "Page",
    table_selector: str,
    *,
    row_selector: str = "tbody tr",
) -> DataSource[dict]:
    """Create data source from HTML table.

    Uses header-based column mapping (reads <th> cells) to map columns by name.
    Skips columns not in schema (e.g., row number '#' column).

    Args:
        page: Async Playwright Page object (caller owns browser lifecycle)
        table_selector: CSS selector for table root element
        row_selector: CSS selector for data rows (default: "tbody tr")

    Returns:
        DataSource yielding dicts matching RPA_CHALLENGE_SCHEMA

    Example:
        # Caller navigates to page and shows table (async)
        await page.goto("http://localhost:8003/?rounds=4")
        await page.click("#toggleDataBtn")

        # Load records from HTML table (async iteration)
        source = from_html_table(page, "table#dataTable")
        records = []
        async for record in source.load():
            records.append(ChallengeRecord.from_dict(record))

        # Or use load_records helper (sync materialization)
        records = load_records(source)
    """
    # Import here to avoid requiring Playwright as a hard dependency
    from .data.sources.html_table import HtmlTableSource

    return HtmlTableSource(
        page,
        table_selector=table_selector,
        row_selector=row_selector,
        schema=RPA_CHALLENGE_SCHEMA,
        header_map=HTML_TABLE_HEADER_MAP,
    )


def load_records(
    source: DataSource,
    *,
    predicate: Callable[[dict], bool] | None = None,
    as_dataclass: bool = True,
) -> list[ChallengeRecord] | list[dict]:
    """Load records from source with optional filtering.

    FUNCTIONAL - no side effects, composable.

    Args:
        source: DataSource to load from.
        predicate: Optional filter function.
        as_dataclass: If True, return ChallengeRecord objects.

    Returns:
        List of records (ChallengeRecord or dict).
    """
    records = source.load()

    if predicate:
        records = (r for r in records if predicate(r))

    if as_dataclass:
        return [ChallengeRecord.from_dict(r) for r in records]
    return list(records)
