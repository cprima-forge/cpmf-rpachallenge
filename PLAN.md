# Architecture Plan: Dual Paradigm Package

## Document Purpose

This document provides specifications for refactoring `cpmf_rpachallenge` to clearly demonstrate **procedural vs functional** programming paradigms side-by-side.

**Target Audience**: Developers implementing this refactor
**Version**: Alpha (open for restructuring)
**Status**: Design spec, not implementation

---

## 1. Vision and Goals

### 1.1 Primary Goal

Enable **learners in advanced upskilling** to see the contrast between procedural and functional programming by:

1. Solving the **same problem two ways**
2. Producing **identical output** from both paths
3. Showing **"how each paradigm looks"** in practice

### 1.2 Design Principle

**"Convenience by default, transparency on demand"**

- **Quick path**: Few lines, just works
- **Learning path**: Caller can "unpack" to see each step
- **Both paths**: Produce identical `list[ChallengeRecord]` output

### 1.3 Future Considerations

The package will eventually be callable by:

| Caller Type | Characteristics |
|-------------|-----------------|
| Human developer | Writes code, controls flow |
| LLM agent | Calls tools, decides next step based on output |
| MCP surface | Exposes resources/tools, structured I/O |

**Implication**: Actions must be discrete, named, describable, with formally declared side effects.

---

## 2. Directory Structure

```
cpmf_rpachallenge/
│
├── actions/                     # All callable actions (verbs)
│   ├── __init__.py              # Exports all actions
│   ├── data.py                  # Data access actions
│   ├── challenge.py             # Challenge solving actions
│   └── _effects.py              # Side effect taxonomy and decorator
│
├── functional/                  # Pure transformations, composable
│   ├── __init__.py              # Convenience exports
│   ├── sources.py               # XlsxSource, HtmlTableSource
│   ├── combinators.py           # filter_records, map_records, collect
│   └── schema.py                # Column, Schema, Parser
│
├── procedural/                  # Imperative orchestration
│   ├── __init__.py              # Convenience exports
│   └── client.py                # RPAChallengeClient (bundled flow)
│
├── domain/                      # rpachallenge-specific (shared by both paradigms)
│   ├── __init__.py              # Convenience exports
│   ├── records.py               # ChallengeRecord, RPA_CHALLENGE_SCHEMA
│   ├── forms.py                 # Selectors, FORM_FIELD_MAP, HTML_TABLE_HEADER_MAP
│   ├── validation.py            # DataValidator (pure)
│   └── results.py               # ResultData, parse_result (pure)
│
├── __init__.py                  # Top-level convenience exports
└── downloads.py                 # DEPRECATED legacy facade
```

---

## 3. Core Contracts

### 3.1 Identical Output Contract

Both paradigms MUST produce identical output:

```python
list[ChallengeRecord]
```

Where `ChallengeRecord` is:

```python
@dataclass
class ChallengeRecord:
    first_name: str
    last_name: str
    company_name: str
    role: str
    address: str
    email: str
    phone: str  # str, not int (form input requires string)

    @classmethod
    def from_dict(cls, data: dict) -> ChallengeRecord: ...

    def as_form_data(self) -> dict[str, str]: ...
```

### 3.2 DataSource Protocol

All functional sources implement:

```python
class DataSource(Protocol[T]):
    def load(self) -> Iterable[T]: ...
```

### 3.3 Combinator Contract

All combinators return `DataSource` (not `Iterable`) for composability:

```python
def filter_records(source: DataSource[T], predicate: Callable[[T], bool]) -> DataSource[T]: ...
def map_records(source: DataSource[T], transform: Callable[[T], T]) -> DataSource[T]: ...
def collect(source: DataSource[T]) -> list[T]: ...
```

**Note**: This requires a wrapper class (e.g., `FilteredSource`, `MappedSource`) that implements `DataSource`.

---

## 4. Side Effect Taxonomy

### 4.1 Effect Categories

```
none        : Pure function, no side effects
network     : HTTP request (GET, POST, etc.)
filesystem  : File read or write
dom_read    : Browser DOM query (non-mutating)
dom_mutate  : Browser DOM modification (click, fill, etc.)
```

### 4.2 Declaration Mechanism

Every action formally declares its side effects via decorator:

```python
@side_effects("network", "filesystem")
def fetch_excel(url: str | None = None, target_dir: Path | None = None) -> Path:
    """Download challenge Excel file."""
    ...
```

The decorator registers metadata accessible at runtime:

```python
fetch_excel.side_effects  # ["network", "filesystem"]
```

### 4.3 Implementation of `_effects.py`

```python
from functools import wraps
from typing import Callable, Literal

Effect = Literal["none", "network", "filesystem", "dom_read", "dom_mutate"]

def side_effects(*effects: Effect) -> Callable:
    """Decorator to declare side effects on a function."""
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        wrapper.side_effects = list(effects)
        return wrapper
    return decorator
```

---

## 5. Action Catalog

### 5.1 Data Access Actions

Located in `actions/data.py`:

| Action | Signature | Returns | Side Effects |
|--------|-----------|---------|--------------|
| `fetch_excel` | `(url?: str, target_dir?: Path) -> Path` | `Path` | `network`, `filesystem` |
| `read_excel` | `(path: Path) -> list[dict]` | `list[dict]` | `filesystem` |
| `parse_html_table` | `(html: str) -> list[dict]` | `list[dict]` | `none` |
| `scrape_table_html` | `(page: Page, selector: str) -> str` | `str` | `dom_read` |
| `scrape_table_rows` | `(page: Page, selector: str) -> list[list[str]]` | `list[list[str]]` | `dom_read` |

**Detailed Specifications**:

#### `fetch_excel`
```python
@side_effects("network", "filesystem")
def fetch_excel(
    url: str | None = None,
    target_dir: Path | None = None,
    config: RpaChallengeConfig | None = None,
) -> Path:
    """
    Download challenge Excel file from URL.

    Args:
        url: Excel file URL. If None, uses config or default.
        target_dir: Directory to save file. If None, uses temp directory.
        config: Configuration object. If None, uses global config.

    Returns:
        Path to downloaded .xlsx file.

    Side effects:
        - network: HTTP GET request
        - filesystem: Creates directory (if needed), writes file

    Raises:
        httpx.HTTPStatusError: If download fails.
    """
```

#### `read_excel`
```python
@side_effects("filesystem")
def read_excel(path: Path) -> list[dict]:
    """
    Read Excel file and return records as dictionaries.

    Args:
        path: Path to .xlsx file.

    Returns:
        List of dicts with keys matching RPA_CHALLENGE_SCHEMA field names.
        Uses header-based column mapping (reads first row as headers).

    Side effects:
        - filesystem: Reads file from disk
    """
```

#### `parse_html_table`
```python
@side_effects("none")
def parse_html_table(html: str) -> list[dict]:
    """
    Parse HTML table string and return records as dictionaries.

    Args:
        html: Raw HTML string containing a <table> element.

    Returns:
        List of dicts with keys matching RPA_CHALLENGE_SCHEMA field names.
        Uses header-based column mapping (reads <th> cells).

    Side effects:
        - none (pure function)

    Note:
        Expects HTML with <thead> containing <th> headers and <tbody> containing <tr> rows.
    """
```

#### `scrape_table_html`
```python
@side_effects("dom_read")
def scrape_table_html(page: Page, selector: str) -> str:
    """
    Extract raw HTML of a table element from a Playwright page.

    Args:
        page: Playwright Page object (caller owns lifecycle).
        selector: CSS selector for table element.

    Returns:
        Raw HTML string of the table element (outerHTML).

    Side effects:
        - dom_read: Queries DOM, waits for element

    Note:
        Caller is responsible for:
        - Browser/page lifecycle
        - Navigation to page
        - Ensuring table is visible/loaded
    """
```

#### `scrape_table_rows`
```python
@side_effects("dom_read")
def scrape_table_rows(
    page: Page,
    selector: str,
    row_selector: str = "tbody tr",
) -> list[list[str]]:
    """
    Extract table rows as list of cell values from a Playwright page.

    Args:
        page: Playwright Page object (caller owns lifecycle).
        selector: CSS selector for table element.
        row_selector: CSS selector for rows within table.

    Returns:
        List of rows, where each row is a list of cell text values.

    Side effects:
        - dom_read: Queries DOM, iterates elements
    """
```

### 5.2 Challenge Actions

Located in `actions/challenge.py`:

| Action | Signature | Returns | Side Effects |
|--------|-----------|---------|--------------|
| `check_ready` | `(page: Page) -> ReadinessResult` | `ReadinessResult` | `dom_read` |
| `start` | `(page: Page) -> bool` | `bool` | `dom_mutate` |
| `fill_form` | `(page: Page, record: ChallengeRecord) -> bool` | `bool` | `dom_mutate` |
| `submit` | `(page: Page) -> bool` | `bool` | `dom_mutate` |
| `get_result` | `(page: Page) -> ResultData` | `ResultData` | `dom_read` |

**Detailed Specifications**:

#### `check_ready`
```python
@side_effects("dom_read")
def check_ready(page: Page) -> ReadinessResult:
    """
    Check if page is ready for automation.

    Args:
        page: Playwright Page object.

    Returns:
        ReadinessResult with:
        - ready: bool
        - issues: list[str] (empty if ready)

    Side effects:
        - dom_read: Checks for presence of required elements
    """
```

#### `start`
```python
@side_effects("dom_mutate")
def start(page: Page) -> bool:
    """
    Click the START button to begin the challenge.

    Args:
        page: Playwright Page object.

    Returns:
        True if start button was clicked successfully.

    Side effects:
        - dom_mutate: Clicks button, triggers page state change
    """
```

#### `fill_form`
```python
@side_effects("dom_mutate")
def fill_form(page: Page, record: ChallengeRecord) -> bool:
    """
    Fill all form fields with record data.

    Args:
        page: Playwright Page object.
        record: ChallengeRecord with field values.

    Returns:
        True if all fields were filled successfully.

    Side effects:
        - dom_mutate: Fills 7 input fields

    Note:
        Uses record.as_form_data() to map fields to ng-reflect-name selectors.
    """
```

#### `submit`
```python
@side_effects("dom_mutate")
def submit(page: Page) -> bool:
    """
    Click the SUBMIT button.

    Args:
        page: Playwright Page object.

    Returns:
        True if submit was successful.

    Side effects:
        - dom_mutate: Clicks submit, triggers form submission
    """
```

#### `get_result`
```python
@side_effects("dom_read")
def get_result(page: Page) -> ResultData:
    """
    Read the challenge result from the page.

    Args:
        page: Playwright Page object.

    Returns:
        ResultData with:
        - success_rate: int (percentage)
        - fields_correct: int
        - total_fields: int
        - time_ms: int
        - raw_message: str

    Side effects:
        - dom_read: Reads result message from DOM
    """
```

### 5.3 Pure Functions (No Side Effects)

Located in `domain/` modules:

| Function | Location | Signature | Returns |
|----------|----------|-----------|---------|
| `validate_records` | `domain/validation.py` | `(records: list[ChallengeRecord]) -> ValidationResult` | `ValidationResult` |
| `to_form_data` | `domain/records.py` | `(record: ChallengeRecord) -> dict[str, str]` | field mapping |
| `parse_result` | `domain/results.py` | `(raw_text: str) -> ResultData` | structured result |
| `from_dict` | `domain/records.py` | `(data: dict) -> ChallengeRecord` | record instance |

---

## 6. Functional Module Specifications

### 6.1 `functional/sources.py`

#### `XlsxSource`

```python
class XlsxSource(DataSource[dict[str, Any]]):
    """
    Excel file data source with schema-driven parsing.

    Reads Excel file from Path, normalizes rows to schema.
    Uses header-based column mapping (not positional).

    Args:
        path: Path to .xlsx file
        schema: Column definitions for parsing
        header_map: Optional mapping of Excel header text to schema field names
                   (e.g., {"First Name": "first_name"})

    Note:
        - File is read on each call to load() (no caching)
        - Header row is row 1, data starts at row 2
    """

    def __init__(
        self,
        path: Path,
        schema: Schema,
        header_map: dict[str, str] | None = None,
    ) -> None: ...

    def load(self) -> Iterable[dict[str, Any]]: ...
```

#### `HtmlTableSource`

```python
class HtmlTableSource(DataSource[dict[str, Any]]):
    """
    HTML table data source with schema-driven parsing.

    Parses raw HTML string, normalizes rows to schema.
    Uses header-based column mapping (reads <th> cells).

    Args:
        html: Raw HTML string containing <table> element
        schema: Column definitions for parsing
        header_map: Optional mapping of HTML header text to schema field names
                   (e.g., {"First Name": "first_name"})

    Note:
        - Pure function (no I/O)
        - Expects <thead> with <th> headers
        - Expects <tbody> with <tr> rows
    """

    def __init__(
        self,
        html: str,
        schema: Schema,
        header_map: dict[str, str] | None = None,
    ) -> None: ...

    def load(self) -> Iterable[dict[str, Any]]: ...
```

### 6.2 `functional/combinators.py`

All combinators return `DataSource` for composability.

```python
class FilteredSource(DataSource[T]):
    """DataSource wrapper that applies a predicate filter."""

    def __init__(self, source: DataSource[T], predicate: Callable[[T], bool]) -> None: ...
    def load(self) -> Iterable[T]: ...


class MappedSource(DataSource[T]):
    """DataSource wrapper that applies a transformation."""

    def __init__(self, source: DataSource[T], transform: Callable[[T], T]) -> None: ...
    def load(self) -> Iterable[T]: ...


def filter_records(source: DataSource[T], predicate: Callable[[T], bool]) -> DataSource[T]:
    """
    Filter records from source (lazy).

    Args:
        source: Input DataSource
        predicate: Function returning True for records to keep

    Returns:
        New DataSource that yields only matching records.
        Lazy - predicate applied during iteration.
    """
    return FilteredSource(source, predicate)


def map_records(source: DataSource[T], transform: Callable[[T], T]) -> DataSource[T]:
    """
    Transform records from source (lazy).

    Args:
        source: Input DataSource
        transform: Function to apply to each record

    Returns:
        New DataSource that yields transformed records.
        Lazy - transform applied during iteration.
    """
    return MappedSource(source, transform)


def collect(source: DataSource[T]) -> list[T]:
    """
    Materialize source into list.

    Args:
        source: Input DataSource

    Returns:
        List containing all records from source.
        Forces evaluation of lazy sources.
    """
    return list(source.load())
```

### 6.3 `functional/schema.py`

```python
from typing import Any, Callable

Parser = Callable[[Any], Any]

@dataclass(frozen=True)
class Column:
    """
    Schema column definition.

    Attributes:
        name: Field name (e.g., "first_name")
        py_type: Python type for parsing (e.g., str, int)
        parser: Optional custom parser function
    """
    name: str
    py_type: type
    parser: Parser | None = None

    def parse(self, value: Any) -> Any:
        """
        Parse raw value to typed value.

        - If value is None, returns None
        - If parser provided, uses parser(value)
        - Otherwise uses py_type(value)
        """
        if value is None:
            return None
        if self.parser is not None:
            return self.parser(value)
        return self.py_type(value)


Schema = list[Column]
```

---

## 7. Domain Module Specifications

### 7.1 `domain/records.py`

```python
# Schema definition (shared by both paradigms)
RPA_CHALLENGE_SCHEMA: Schema = [
    Column("first_name", str),
    Column("last_name", str),
    Column("company_name", str),
    Column("role", str),
    Column("address", str),
    Column("email", str),
    Column("phone", str),  # str, not int
]

# Form field mapping (ng-reflect-name values)
FORM_FIELD_MAP: dict[str, str] = {
    "first_name": "labelFirstName",
    "last_name": "labelLastName",
    "company_name": "labelCompanyName",
    "role": "labelRole",
    "address": "labelAddress",
    "email": "labelEmail",
    "phone": "labelPhone",
}

# Excel header mapping
EXCEL_HEADER_MAP: dict[str, str] = {
    "First Name": "first_name",
    "Last Name": "last_name",
    "Phone Number": "phone",
    "Email": "email",
    "Address": "address",
    "Company Name": "company_name",
    "Role in Company": "role",
}

# HTML table header mapping
HTML_TABLE_HEADER_MAP: dict[str, str] = {
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
    """Canonical record type for rpachallenge.com."""

    first_name: str
    last_name: str
    company_name: str
    role: str
    address: str
    email: str
    phone: str

    @classmethod
    def from_dict(cls, data: dict) -> "ChallengeRecord":
        """Create from dictionary (keys must match schema field names)."""
        ...

    def as_form_data(self) -> dict[str, str]:
        """Map to form field names (ng-reflect-name values)."""
        ...
```

---

## 8. Responsibility Matrix

### 8.1 Data Access Responsibilities

| Concern | Procedural | Functional | Domain | Caller |
|---------|------------|------------|--------|--------|
| **Excel: HTTP download** | `actions/data.fetch_excel` | — | — | optional |
| **Excel: File read** | `actions/data.read_excel` | `XlsxSource(Path)` | — | — |
| **Excel: Header mapping** | — | — | `EXCEL_HEADER_MAP` | — |
| **Excel: Row → dict** | `read_excel` (inline) | `XlsxSource.load()` | schema | — |
| **HTML: Fetch raw string** | `actions/data.scrape_table_html` | — | — | ✓ |
| **HTML: Parse string → rows** | `actions/data.parse_html_table` | `HtmlTableSource(str)` | schema | — |
| **HTML: Header mapping** | — | — | `HTML_TABLE_HEADER_MAP` | — |
| **HTML: Row → dict** | `parse_html_table` (inline) | `HtmlTableSource.load()` | schema | — |
| **DOM: Page navigation** | — | — | — | ✓ |
| **DOM: Extract table HTML** | `actions/data.scrape_table_html` | — | — | ✓ |
| **DOM: Extract table rows** | `actions/data.scrape_table_rows` | — | — | ✓ |
| **dict → ChallengeRecord** | inline | `ChallengeRecord.from_dict` | `records.py` | — |
| **Filtering** | `for` loop | `filter_records()` | — | — |
| **Mapping/transform** | `for` loop | `map_records()` | — | — |
| **Materialization** | implicit | `collect()` | — | — |

### 8.2 Challenge Solving Responsibilities

| Concern | Procedural | Functional | Domain | Caller |
|---------|------------|------------|--------|--------|
| **Page lifecycle** | — | — | — | ✓ |
| **Navigate to URL** | `procedural/client.py` | — | config | ✓ |
| **Check readiness** | `actions/challenge.check_ready` | `actions/challenge.check_ready` | `ReadinessResult` | — |
| **Click START** | `actions/challenge.start` | `actions/challenge.start` | selectors | — |
| **Map record → form data** | `record.as_form_data()` | `record.as_form_data()` | `records.py` | — |
| **Fill form fields** | `actions/challenge.fill_form` | `actions/challenge.fill_form` | selectors | — |
| **Click SUBMIT** | `actions/challenge.submit` | `actions/challenge.submit` | selectors | — |
| **Iteration control** | `procedural/client` (internal) | — | — | ✓ |
| **Completion decision** | `procedural/client` (internal) | — | — | ✓ |
| **Read result** | `actions/challenge.get_result` | `actions/challenge.get_result` | `ResultData` | — |
| **Parse result text** | — | `parse_result()` | `results.py` | — |
| **Validation** | — | `validate_records()` | `validation.py` | — |

---

## 9. Usage Examples

### 9.1 Quick Path (Convenience)

```python
from cpmf_rpachallenge import get_challenge_records, solve_challenge

# Data access
records = get_challenge_records()

# Or full solve
result = solve_challenge(page)
print(f"Score: {result.success_rate}%")
```

### 9.2 Procedural Path (Step-by-Step)

```python
from cpmf_rpachallenge.actions import (
    fetch_excel, read_excel, start, fill_form, submit, get_result
)
from cpmf_rpachallenge.domain import ChallengeRecord

# Step 1: Download Excel (side effect: network, filesystem)
path = fetch_excel()

# Step 2: Parse Excel (side effect: filesystem)
dicts = read_excel(path)

# Step 3: Convert to records (inline)
records = [ChallengeRecord.from_dict(d) for d in dicts]

# Step 4: Filter (imperative loop)
managers = []
for record in records:
    if record.role == "Manager":
        managers.append(record)

# Step 5: Solve challenge (side effects: dom_mutate)
start(page)
for record in managers:
    fill_form(page, record)
    submit(page)

# Step 6: Get result (side effect: dom_read)
result = get_result(page)
print(f"Score: {result.success_rate}%")
```

### 9.3 Functional Path (Pipeline)

```python
from cpmf_rpachallenge.functional import XlsxSource, filter_records, collect
from cpmf_rpachallenge.domain import (
    RPA_CHALLENGE_SCHEMA, EXCEL_HEADER_MAP, ChallengeRecord
)
from cpmf_rpachallenge.actions import fetch_excel, start, fill_form, submit, get_result

# Step 1: I/O at boundary
path = fetch_excel()

# Step 2: Create source (pure)
source = XlsxSource(path, RPA_CHALLENGE_SCHEMA, header_map=EXCEL_HEADER_MAP)

# Step 3: Compose transformations (pure, lazy)
filtered = filter_records(source, lambda r: r["role"] == "Manager")

# Step 4: Materialize (pure)
dicts = collect(filtered)

# Step 5: Convert to domain type (pure)
records = [ChallengeRecord.from_dict(d) for d in dicts]

# Step 6: Solve (caller controls iteration)
start(page)
for record in records:
    fill_form(page, record)
    submit(page)

result = get_result(page)
```

### 9.4 HTML Table Path (Both Paradigms)

**Procedural:**
```python
from cpmf_rpachallenge.actions import scrape_table_html, parse_html_table, start, fill_form, submit

# Caller navigates
await page.goto("http://rpachallenge.com")
await page.click("#showData")

# Scrape HTML (side effect: dom_read)
html = scrape_table_html(page, "table#dataTable")

# Parse (pure)
dicts = parse_html_table(html)
records = [ChallengeRecord.from_dict(d) for d in dicts]

# Solve
start(page)
for record in records:
    fill_form(page, record)
    submit(page)
```

**Functional:**
```python
from cpmf_rpachallenge.functional import HtmlTableSource, filter_records, collect
from cpmf_rpachallenge.domain import RPA_CHALLENGE_SCHEMA, HTML_TABLE_HEADER_MAP

# Caller fetches HTML (I/O at boundary)
await page.goto("http://rpachallenge.com")
await page.click("#showData")
html = await page.locator("table#dataTable").inner_html()

# Pure pipeline
source = HtmlTableSource(html, RPA_CHALLENGE_SCHEMA, header_map=HTML_TABLE_HEADER_MAP)
filtered = filter_records(source, lambda r: r["role"] == "Manager")
dicts = collect(filtered)
records = [ChallengeRecord.from_dict(d) for d in dicts]
```

### 9.5 LLM Agent Usage (Future)

```python
# Agent calls actions discretely, decides each step

# Agent: "I'll fetch the data first"
path = fetch_excel()  # Returns Path

# Agent: "Now I'll read and validate"
dicts = read_excel(path)  # Returns list[dict]
records = [ChallengeRecord.from_dict(d) for d in dicts]
validation = validate_records(records)

if not validation.valid:
    # Agent: "Data invalid, I'll report the issues"
    return {"error": validation.issues}

# Agent: "Data valid, I'll solve the challenge"
ready = check_ready(page)
if not ready.ready:
    # Agent: "Page not ready"
    return {"error": ready.issues}

start(page)
for record in records:
    fill_form(page, record)
    submit(page)

result = get_result(page)
# Agent: "Challenge complete, returning result"
return {"success_rate": result.success_rate, "time_ms": result.time_ms}
```

---

## 10. Migration Path

### 10.1 Files to Create

| File | Priority | Description |
|------|----------|-------------|
| `actions/__init__.py` | HIGH | Export all actions |
| `actions/data.py` | HIGH | Data access actions |
| `actions/challenge.py` | HIGH | Challenge solving actions |
| `actions/_effects.py` | HIGH | Side effect decorator |
| `functional/sources.py` | HIGH | XlsxSource, HtmlTableSource (refactor existing) |
| `functional/combinators.py` | HIGH | filter_records, map_records, collect (refactor existing) |
| `procedural/__init__.py` | MEDIUM | Convenience exports |
| `domain/__init__.py` | MEDIUM | Convenience exports |

### 10.2 Files to Refactor

| File | Changes |
|------|---------|
| `data/sources/xlsx.py` | Move domain-specific `excel_to_schema` mapping to `domain/records.py` |
| `data/sources/html_table.py` | Rename to `HtmlTableSource`, accept `str` instead of `Page` |
| `data/protocol.py` | Ensure combinators return `DataSource` |
| `records.py` | Move to `domain/records.py`, add header mappings |
| `fetch.py` | Move to `actions/data.py` |
| `client.py` | Move to `procedural/client.py` |

### 10.3 Files to Deprecate

| File | Status |
|------|--------|
| `downloads.py` | Already deprecated, keep for backwards compatibility |

---

## 11. Testing Requirements

### 11.1 Paradigm Equivalence Tests

```python
def test_excel_procedural_equals_functional():
    """Both paths produce identical records from Excel."""
    # Procedural
    path = fetch_excel()
    procedural_records = [ChallengeRecord.from_dict(d) for d in read_excel(path)]

    # Functional
    source = XlsxSource(path, RPA_CHALLENGE_SCHEMA, header_map=EXCEL_HEADER_MAP)
    functional_records = [ChallengeRecord.from_dict(d) for d in collect(source)]

    assert procedural_records == functional_records


def test_html_procedural_equals_functional():
    """Both paths produce identical records from HTML."""
    html = "<table>...</table>"

    # Procedural
    procedural_records = [ChallengeRecord.from_dict(d) for d in parse_html_table(html)]

    # Functional
    source = HtmlTableSource(html, RPA_CHALLENGE_SCHEMA, header_map=HTML_TABLE_HEADER_MAP)
    functional_records = [ChallengeRecord.from_dict(d) for d in collect(source)]

    assert procedural_records == functional_records
```

### 11.2 Combinator Composability Tests

```python
def test_filter_returns_datasource():
    """filter_records returns DataSource, not Iterable."""
    source = XlsxSource(path, schema)
    filtered = filter_records(source, lambda r: True)

    assert isinstance(filtered, DataSource)

    # Can compose further
    double_filtered = filter_records(filtered, lambda r: True)
    assert isinstance(double_filtered, DataSource)


def test_combinators_are_lazy():
    """Combinators don't evaluate until collect()."""
    call_count = 0

    def counting_predicate(r):
        nonlocal call_count
        call_count += 1
        return True

    source = XlsxSource(path, schema)
    filtered = filter_records(source, counting_predicate)

    assert call_count == 0  # Not evaluated yet

    collect(filtered)
    assert call_count > 0  # Now evaluated
```

### 11.3 Side Effect Declaration Tests

```python
def test_actions_declare_side_effects():
    """All actions have side_effects attribute."""
    from cpmf_rpachallenge.actions import fetch_excel, read_excel, parse_html_table

    assert fetch_excel.side_effects == ["network", "filesystem"]
    assert read_excel.side_effects == ["filesystem"]
    assert parse_html_table.side_effects == ["none"]
```

---

## 12. Open Questions

1. **Async support**: Should functional sources have async `load()` for HTML tables scraped via Playwright?
   - Current decision: No, HTML source accepts string (already fetched)

2. **Error handling**: Should actions raise exceptions or return Result types?
   - Current decision: Raise exceptions (keep it simple for learning)

3. **Configuration injection**: How should actions access config?
   - Current decision: Optional `config` parameter with fallback to global

---

## 13. Success Criteria

1. **Learner can see both paradigms**: Side-by-side code clearly shows procedural vs functional
2. **Identical output**: Both paths produce same `list[ChallengeRecord]`
3. **Composable functional path**: `filter_records(filter_records(source, p1), p2)` works
4. **Declared side effects**: Every action has `side_effects` attribute
5. **Future-ready**: Actions are discrete enough for LLM agent / MCP exposure

---

*End of Plan*
