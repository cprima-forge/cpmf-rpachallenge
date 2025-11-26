# cpmf-rpachallenge

Playwright selectors and utilities for automating [rpachallenge.com](https://rpachallenge.com).

## Installation

```bash
pip install cpmf-rpachallenge
```

## Usage

```python
from cpmf_rpachallenge import Downloads, FormFields, Buttons, Results

# Fetch and parse Excel data in one call
records = Downloads.get_challenge_data()

# Use with Playwright
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    await page.goto("https://rpachallenge.com")

    # Click START
    await page.click(Buttons.START)

    # Fill and submit for each record
    for record in records:
        for field_name, value in record.as_form_data().items():
            await page.fill(f'input[ng-reflect-name="{field_name}"]', value)
        await page.click(Buttons.SUBMIT)

    # Get results
    message = await page.inner_text(Results.MESSAGE_DETAILS)
    result = Results.parse_results(message)
    print(f"Score: {result.success_rate}% in {result.time_seconds}s")

    await browser.close()
```

## API Reference

### FormFields

Stable selectors using `ng-reflect-name` attributes:

- `FormFields.FIRST_NAME`
- `FormFields.LAST_NAME`
- `FormFields.PHONE`
- `FormFields.EMAIL`
- `FormFields.ADDRESS`
- `FormFields.COMPANY_NAME`
- `FormFields.ROLE`

### Buttons

- `Buttons.START` - Start button
- `Buttons.SUBMIT` - Submit button
- `Buttons.RESET` - Reset button (same element as START)

### Downloads

- `Downloads.fetch_excel(target_dir=None)` - Download Excel to temp/custom dir
- `Downloads.get_challenge_data()` - Fetch Excel and return list of `ChallengeRecord`
- `Downloads.EXCEL_URL` - Direct URL to Excel file

### ChallengeRecord

Dataclass with fields: `first_name`, `last_name`, `company_name`, `role`, `address`, `email`, `phone`

- `record.as_form_data()` - Returns dict with `ng-reflect-name` keys

### Results

- `Results.MESSAGE_DETAILS` - Selector for results message
- `Results.parse_results(message)` - Parse message into `ResultData`

### ResultData

Dataclass with: `success_rate`, `fields_correct`, `total_fields`, `time_ms`, `raw_message`

- `result.time_seconds` - Time in seconds (float)

### ReadinessCheck

Verifies that the rpachallenge.com page is ready for automation before proceeding.

```python
from cpmf_rpachallenge import ReadinessCheck

# Async usage
result = await ReadinessCheck.run_async(page)
if result.is_automatable:
    # Proceed with automation
    pass
else:
    print(f"Page not ready: {result.summary}")
    for name in result.failed_checks:
        print(f"  - {result.checks[name].message}")

# Sync usage
result = ReadinessCheck.run(page)
if not result.is_automatable:
    raise RuntimeError(result.summary)

# Check only specific elements
result = await ReadinessCheck.run_async(page, checks=["excel_link", "start_button"])
```

### ReadinessResult

Dataclass returned by `ReadinessCheck.run()` / `ReadinessCheck.run_async()`:

- `is_automatable` - `True` if all checks passed
- `checks` - Dict of check name to `CheckStatus`
- `failed_checks` - List of check names that failed
- `passed_checks` - List of check names that passed
- `summary` - Human-readable summary string

### CheckStatus

Dataclass for individual check results:

- `name` - Check name (e.g., "excel_link", "first_name")
- `passed` - `True` if element was found
- `selector` - CSS selector used
- `message` - Error message if failed, `None` if passed

### ScreenshotCapture

Capture screenshots during automation with support for PNG, JPEG, and PDF formats.

```python
from cpmf_rpachallenge import ScreenshotCapture, ScreenshotFormat

# Initialize capture
capture = ScreenshotCapture()

# Take screenshots during automation
for i, record in enumerate(records):
    # Fill form...
    await capture.take_async(page, label=f"form_{i}_filled")
    await page.click(Buttons.SUBMIT)

# Capture result page
await capture.take_async(page, label="result", full_page=True)

# Take PDF (Chromium only)
await capture.take_pdf_async(page, label="result_pdf")

# Save all screenshots
paths = capture.collection.save_all("./screenshots")

# Create montage (requires pillow)
montage = capture.collection.create_montage(columns=5, padding=10)
Path("montage.png").write_bytes(montage)

# Create vertical strip of just form screenshots
strip = capture.collection.create_vertical_strip(
    labels=["form_0_filled", "form_1_filled", "form_2_filled"]
)
```

### Screenshot

Individual screenshot object:

- `data` - Raw bytes of the screenshot
- `format` - `ScreenshotFormat.PNG`, `JPEG`, or `PDF`
- `label` - User-provided label
- `index` - Sequential index
- `save(path)` - Save to file
- `to_pil_image()` - Convert to PIL Image (PNG/JPEG only)

### ScreenshotCollection

Collection with montage capabilities:

- `save_all(directory, prefix)` - Save all screenshots to directory
- `create_montage(columns, padding, background_color, labels)` - Create grid image
- `create_vertical_strip(...)` - Single column montage
- `create_horizontal_strip(...)` - Single row montage
- `get_by_label(label)` - Filter screenshots by label

### ScreenshotFormat

Enum for screenshot formats:

- `ScreenshotFormat.PNG` - Lossless, larger files
- `ScreenshotFormat.JPEG` - Lossy, smaller files
- `ScreenshotFormat.PDF` - PDF document (Chromium only)

### DataValidator

Validate Excel data before automation:

```python
from cpmf_rpachallenge import Downloads, DataValidator

records = Downloads.get_challenge_data()
result = DataValidator.validate(records)

if not result.is_valid:
    print(f"Data issues: {result.summary}")
    for record in result.invalid_records:
        print(f"  {record.summary}")
        for error in record.errors:
            print(f"    - {error.field}: {error.message}")
    # Decide: abort, skip invalid records, or proceed anyway

# Quick check
if DataValidator.is_valid(records):
    # Proceed with automation
    pass
```

### DataValidationResult

Result from `DataValidator.validate()`:

- `is_valid` - `True` if all records valid and count matches expected
- `record_count` - Number of records found
- `expected_count` - Expected number (default: 10)
- `valid_count` / `invalid_count` - Count by validity
- `invalid_records` - List of `RecordValidationResult` with errors
- `total_errors` - Total error count across all records
- `summary` - Human-readable summary

### RecordValidationResult

Validation result for a single record:

- `index` - Record index (0-based)
- `is_valid` - `True` if record has no errors
- `errors` - List of `FieldError` objects
- `summary` - Human-readable summary

### FieldError

Individual field validation error:

- `field` - Field name (e.g., "email", "phone")
- `value` - The invalid value
- `message` - Error description

### Validation Rules

| Field | Rule |
|-------|------|
| All fields | Required (non-empty) |
| `email` | Must match `^[^@\s]+@[^@\s]+\.[^@\s]+$` |
| `phone` | Must contain at least 7 digits |
| Record count | Must equal expected (default: 10) |

## Configuration

Configuration uses a hierarchy (highest to lowest priority):
1. Explicit parameters passed to functions
2. Environment variables (`RPACHALLENGE_*`)
3. Default values

**Note:** This library does NOT auto-load `.env` files. Load them in your application using `python-dotenv` or similar before importing this library.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RPACHALLENGE_BASE_URL` | `https://rpachallenge.com` | Base URL |
| `RPACHALLENGE_EXCEL_URL` | `https://rpachallenge.com/assets/downloadFiles/challenge.xlsx` | Excel download URL |
| `RPACHALLENGE_HEADLESS` | `true` | Run browser headless |
| `RPACHALLENGE_TIMEOUT_MS` | `30000` | Timeout in milliseconds |
| `RPACHALLENGE_DOWNLOAD_DIR` | (temp dir) | Download directory |
| `RPACHALLENGE_SLOW_MO` | `0` | Slow motion delay (ms) |

### Using Config in Code

```python
from cpmf_rpachallenge import get_config, RpaChallengeConfig, Downloads

# Get global config (reads from environment variables)
config = get_config()
print(f"Headless: {config.headless}")

# Create custom config directly
custom_config = RpaChallengeConfig(
    headless=False,
    slow_mo=100,  # Slow down for debugging
)

# Use config with downloads
records = Downloads.get_challenge_data(config=custom_config)

# Override specific values from existing config
debug_config = config.with_overrides(headless=False, slow_mo=50)
```

### Using with .env files

If you want `.env` support, load it in your application:

```python
# In your application (not the library)
from dotenv import load_dotenv
load_dotenv()  # Load before importing cpmf_rpachallenge

from cpmf_rpachallenge import get_config
config = get_config()  # Now reads from .env via os.environ
```

## License

Apache-2.0
