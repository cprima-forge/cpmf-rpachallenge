# cpmf-rpachallenge

Playwright selectors and utilities for automating [rpachallenge.com](https://rpachallenge.com).

**Version 0.3.0** - Complete architectural refactoring with functional and procedural paradigms.

## Installation

```bash
pip install cpmf-rpachallenge
```

## Breaking Changes in 0.3.0

This release introduces a complete architectural refactoring:

- **New directory structure**: Code organized into `procedural/`, `functional/`, `actions/`, and `domain/`
- **Pure functional data sources**: `HtmlTableSource` is now sync and accepts HTML strings (no async I/O)
- **Side effects taxonomy**: Actions are decorated with `@side_effects()` to declare I/O operations
- **Deprecated APIs**: Old imports still work but issue `DeprecationWarning`

### Migration Guide

**Old (Deprecated):**
```python
from cpmf_rpachallenge import Downloads, FormFields, Buttons
from cpmf_rpachallenge import from_html_table  # REMOVED

records = Downloads.get_challenge_data()
await page.fill(FormFields.FIRST_NAME, "John")
```

**New (Recommended):**
```python
from cpmf_rpachallenge.domain import from_xlsx, load_records
from cpmf_rpachallenge.domain.selectors import Pages
from cpmf_rpachallenge.actions import scrape_table_html, parse_html_table
from cpmf_rpachallenge import fetch_challenge_excel

path = fetch_challenge_excel()
source = from_xlsx(path)
records = load_records(source)

await page.fill(Pages.ChallengePage.Fields.FIRST_NAME, "John")

# HTML table scraping (two-step: scrape + parse)
html = await scrape_table_html(page, "table#dataTable")  # I/O action
dicts = parse_html_table(html)  # Pure transformation
records = [ChallengeRecord.from_dict(d) for d in dicts]
```

## Architecture

The library is organized into four layers:

- **procedural/** - Imperative, step-by-step workflows (RPAChallengeClient)
- **functional/** - Pure transformations, composable data sources
- **actions/** - Discrete I/O operations with declared side effects
- **domain/** - Business logic, schemas, validation, results, selectors
- **backends/** - Driver implementations (Playwright, API)

## Quick Start (Procedural)

High-level client for imperative workflows:

```python
from cpmf_rpachallenge.procedural import RPAChallengeClient
from cpmf_rpachallenge.backends import PlaywrightBackend
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    await page.goto("https://rpachallenge.com")

    backend = PlaywrightBackend(page)
    client = RPAChallengeClient(backend=backend)

    # Run complete challenge
    result = await client.run_async()
    print(f"Score: {result.success_rate}% in {result.time_ms}ms")

    await browser.close()
```

## Quick Start (Functional)

Composable data sources and pure transformations:

```python
from cpmf_rpachallenge import fetch_challenge_excel
from cpmf_rpachallenge.domain import from_xlsx, load_records, ChallengeRecord
from cpmf_rpachallenge.functional import filter_records
from cpmf_rpachallenge.domain.selectors import Pages
from playwright.async_api import async_playwright

# Functional data access
path = fetch_challenge_excel()
source = from_xlsx(path)

# Composable filtering
filtered = filter_records(source, lambda r: r["role"] == "Manager")
records = load_records(filtered, as_dataclass=True)

# Use with Playwright
async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    await page.goto("https://rpachallenge.com")

    await page.click(Pages.ChallengePage.Buttons.START)

    for record in records:
        for field_name, value in record.as_form_data().items():
            await page.fill(f'input[ng-reflect-name="{field_name}"]', value)
        await page.click(Pages.ChallengePage.Buttons.SUBMIT)

    # Parse results
    message = await page.inner_text(Pages.ChallengePage.Results.MESSAGE_DETAILS)
    result = Results.parse_results(message)
    print(f"Score: {result.success_rate}%")

    await browser.close()
```

## API Reference

### Domain Layer

#### Page Selectors (Page Object Pattern)

```python
from cpmf_rpachallenge.domain.selectors import Pages

# Challenge page (main form)
Pages.ChallengePage.Fields.FIRST_NAME
Pages.ChallengePage.Fields.LAST_NAME
Pages.ChallengePage.Fields.PHONE
Pages.ChallengePage.Fields.EMAIL
Pages.ChallengePage.Fields.ADDRESS
Pages.ChallengePage.Fields.COMPANY_NAME
Pages.ChallengePage.Fields.ROLE

Pages.ChallengePage.Buttons.START
Pages.ChallengePage.Buttons.SUBMIT
Pages.ChallengePage.Buttons.RESET

Pages.ChallengePage.Results.MESSAGE_CONTAINER
Pages.ChallengePage.Results.MESSAGE_TITLE
Pages.ChallengePage.Results.MESSAGE_DETAILS

# Data table page (paginated tables)
Pages.DataTablePage.TABLE
Pages.DataTablePage.HEADERS
Pages.DataTablePage.ROWS
Pages.DataTablePage.Navigation.NEXT
Pages.DataTablePage.Navigation.PREV
```

#### Records and Schemas

```python
from cpmf_rpachallenge.domain import (
    ChallengeRecord,
    RPA_CHALLENGE_SCHEMA,
    from_xlsx,
    load_records,
)

# Load from Excel
source = from_xlsx("challenge.xlsx")
records = load_records(source)

# Create record
record = ChallengeRecord(
    first_name="John",
    last_name="Doe",
    company_name="Acme Corp",
    role="Developer",
    address="123 Main St",
    email="john@example.com",
    phone="1234567890",
)

# Convert to form data
form_data = record.as_form_data()  # {"labelFirstName": "John", ...}
```

#### Validation

```python
from cpmf_rpachallenge.domain import DataValidator

records = load_records(from_xlsx("challenge.xlsx"))
result = DataValidator.validate(records)

if not result.is_valid:
    print(f"Data issues: {result.summary}")
    for record in result.invalid_records:
        print(f"  {record.summary}")
        for error in record.errors:
            print(f"    - {error.field}: {error.message}")
```

#### Results

```python
from cpmf_rpachallenge.domain import Results

message = await page.inner_text(Pages.ChallengePage.Results.MESSAGE_DETAILS)
result = Results.parse_results(message)

print(f"Success rate: {result.success_rate}%")
print(f"Time: {result.time_seconds}s")
print(f"Fields correct: {result.fields_correct}/{result.total_fields}")
```

### Functional Layer

#### Data Sources

```python
from cpmf_rpachallenge.functional import XlsxSource, HtmlTableSource
from cpmf_rpachallenge.domain import RPA_CHALLENGE_SCHEMA, EXCEL_HEADER_MAP

# Excel source (pure, sync)
source = XlsxSource("challenge.xlsx", RPA_CHALLENGE_SCHEMA, header_map=EXCEL_HEADER_MAP)
for record in source.load():
    print(record)

# HTML table source (pure, sync - accepts HTML string)
html = "<table>...</table>"
source = HtmlTableSource(html, RPA_CHALLENGE_SCHEMA, header_map=HTML_TABLE_HEADER_MAP)
records = list(source.load())
```

#### Combinators

```python
from cpmf_rpachallenge.functional import filter_records, map_records, collect

# Composable filtering
source = from_xlsx("challenge.xlsx")
filtered = filter_records(source, lambda r: r["role"] == "Manager")
records = collect(filtered)

# Composable mapping
mapped = map_records(filtered, lambda r: {**r, "full_name": f"{r['first_name']} {r['last_name']}"})
records = collect(mapped)
```

### Actions Layer

Actions handle I/O boundaries and are decorated with `@side_effects()`:

```python
from cpmf_rpachallenge.actions import scrape_table_html, parse_html_table, read_excel

# DOM I/O action (async)
html = await scrape_table_html(page, "table#dataTable")

# Pure transformation (sync)
dicts = parse_html_table(html)

# File system action (sync)
dicts = read_excel("challenge.xlsx")
```

### Procedural Layer

High-level client for imperative workflows:

```python
from cpmf_rpachallenge.procedural import RPAChallengeClient

backend = PlaywrightBackend(page)
client = RPAChallengeClient(backend=backend)

# High-level operations
records = client.get_records()
validation = client.validate_records(records)

if validation.is_valid:
    client.start()
    for record in records:
        client.fill_form(record)
        client.submit()
    result = client.get_result()
```

### Readiness Checks

```python
from cpmf_rpachallenge.domain import ReadinessCheck

result = await ReadinessCheck.run_async(page)
if result.is_automatable:
    # Proceed with automation
    pass
else:
    print(f"Page not ready: {result.summary}")
    for name in result.failed_checks:
        print(f"  - {result.checks[name].message}")
```

### Screenshots

```python
from cpmf_rpachallenge import ScreenshotCapture, ScreenshotFormat

capture = ScreenshotCapture()

# Capture screenshots
await capture.take_async(page, label="form_filled")
await capture.take_pdf_async(page, label="result_pdf")

# Save all
paths = capture.collection.save_all("./screenshots")

# Create montage
montage = capture.collection.create_montage(columns=5)
Path("montage.png").write_bytes(montage)
```

## Configuration

Configuration hierarchy (highest to lowest priority):
1. Explicit parameters passed to functions
2. Environment variables (`RPACHALLENGE_*`)
3. Default values

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RPACHALLENGE_BASE_URL` | `https://rpachallenge.com` | Base URL |
| `RPACHALLENGE_EXCEL_URL` | `https://rpachallenge.com/assets/downloadFiles/challenge.xlsx` | Excel download URL |
| `RPACHALLENGE_HEADLESS` | `true` | Run browser headless |
| `RPACHALLENGE_TIMEOUT_MS` | `30000` | Timeout in milliseconds |
| `RPACHALLENGE_DOWNLOAD_DIR` | (temp dir) | Download directory |
| `RPACHALLENGE_SLOW_MO` | `0` | Slow motion delay (ms) |

### Using Config

```python
from cpmf_rpachallenge import get_config, RpaChallengeConfig

config = get_config()  # Reads from environment
custom = RpaChallengeConfig(headless=False, slow_mo=100)
debug = config.with_overrides(headless=False)
```

## Deprecated APIs

These APIs still work but issue `DeprecationWarning`:

```python
# DEPRECATED - use domain.selectors.Pages instead
from cpmf_rpachallenge import FormFields, Buttons

# DEPRECATED - use domain imports
from cpmf_rpachallenge import ChallengeRecord, DataValidator

# DEPRECATED - use fetch_challenge_excel() + from_xlsx()
from cpmf_rpachallenge import Downloads
```

## License

Apache-2.0
