# Code Review: Procedural vs Functional Paths

**Reviewer:** Claude
**Date:** 2025-11-27
**Scope:** Assess that `cpmf_rpachallenge` cleanly supports both procedural and functional paths

---

## Executive Summary

The dual architecture has been **substantially implemented**. The codebase now has:
- A generic `data/` layer that is domain-agnostic
- A `fetch.py` module for procedural HTTP/filesystem operations
- A `records.py` module for domain-specific schema and record types
- A deprecated `downloads.py` facade for backwards compatibility

**Overall Assessment: GOOD with minor issues noted below.**

---

## 2. Data Layer (`cpmf_rpachallenge/data`)

### 2.1 `data/__init__.py`

**File:** `src/cpmf_rpachallenge/data/__init__.py`

**Checks:**

- [x] Exports only generic abstractions
- [x] Contains no rpachallenge-specific imports
- [x] `__all__` lists match exports

**Current exports (lines 11-24):**
```python
__all__ = [
    "DataSource",
    "Column", "Schema", "Parser",
    "XlsxSource",
    "filter_records", "map_records", "collect",
]
```

**PASS** - No issues found.

---

### 2.2 `protocol.py`

**File:** `src/cpmf_rpachallenge/data/protocol.py`

**Checks:**

- [x] `DataSource` is a `Protocol` with `load() -> Iterable[T]` (line 11-16)
- [x] Type var `T` bounded as `Mapping[str, Any]` (line 8)
- [x] `filter_records` uses `predicate` parameter (line 24)
- [x] `map_records` uses `transform` parameter (line 34)
- [x] No domain imports

**Issues Found:**

1. **TODO (minor):** `filter_records` returns `Iterable[T]` not a `DataSource[T]` (line 25)
   - This breaks composability: `filter_records(filter_records(source, p1), p2)` won't work
   - The brief expected `filter_records` to return a new `DataSource`
   - **Recommendation:** Create wrapper class or keep as-is (current design is simpler)

2. **TODO (minor):** Same issue with `map_records` (line 35)

**Current implementation (lines 22-38):**
```python
def filter_records(source: DataSource[T], predicate: ...) -> Iterable[T]:
    for record in source.load():
        if predicate(record):
            yield record

def map_records(source: DataSource[T], transform: ...) -> Iterable[T]:
    for record in source.load():
        yield transform(record)
```

**PASS with notes** - Functionally correct, but not fully composable as DataSources.

---

### 2.3 `schema.py`

**File:** `src/cpmf_rpachallenge/data/schema.py`

**Checks:**

- [x] `Column` is frozen (`frozen=True`) (line 12)
- [x] Has `name: str`, `py_type: type`, `parser: Parser | None = None` (lines 16-18)
- [x] `parse()` handles `None` safely (line 22)
- [x] Uses `parser` if provided, else `py_type(value)` (lines 24-26)
- [x] `Schema = list[Column]` defined (line 30)
- [x] No domain imports

**PASS** - No issues found.

---

### 2.4 `sources/xlsx.py`

**File:** `src/cpmf_rpachallenge/data/sources/xlsx.py`

**Checks:**

- [x] Uses `openpyxl` (line 9)
- [x] `XlsxSource(path, schema, ...)` constructor (lines 26-37)
- [x] `load()` yields `dict[str, Any]` records (line 39)
- [x] Applies `Column.parse()` via `row_to_dict` (line 18-20)
- [x] Configurable `data_start_row` parameter (line 32)
- [x] No rpachallenge-specific logic

**PASS** - No issues found.

---

### 2.5 `sources/html.py`

**File:** `src/cpmf_rpachallenge/data/sources/html.py`

**Issues Found:**

1. **WARNING:** This file imports `playwright` (line 3)
   ```python
   from playwright.sync_api import Locator, Page
   ```
   - This is a **domain-specific driver dependency** in the generic data layer
   - Violates the principle that `data/` should be domain-agnostic

2. **TODO:** Move `iter_normalized_rows` to `backends/` or a separate `playwright_utils.py`
   - The function is Playwright-specific, not a generic data source

**FAIL** - Domain leakage in generic data layer.

---

## 3. Procedural vs Functional Split

### 3.1 Procedural: `fetch.py`

**File:** `src/cpmf_rpachallenge/fetch.py`

**Checks:**

- [x] `fetch_challenge_excel` and `fetch_challenge_excel_async` defined (lines 15, 35)
- [x] Performs only: config resolution, HTTP GET, directory/file creation, writing bytes (lines 20-32)
- [x] Returns `Path` only (lines 32, 53)
- [x] No mention of `ChallengeRecord`, schema, parsing, or `openpyxl`
- [x] Uses `RpaChallengeConfig` + `get_config()` correctly (line 20, 40)
- [x] Calls `.raise_for_status()` (lines 30, 51)

**Docstring discipline (line 3-4):**
```python
"""DISCIPLINE: No parsing, no schema, no ChallengeRecord.
Only: config → download → return Path."""
```

**PASS** - Excellent separation of concerns.

---

### 3.2 Functional: `records.py`

**File:** `src/cpmf_rpachallenge/records.py`

**Checks:**

- [x] `RPA_CHALLENGE_SCHEMA` uses correct types (lines 13-21)
- [x] `phone` is `str` not `int` (line 20) - with comment explaining why
- [x] `ChallengeRecord` is canonical domain dataclass (lines 35-54)
- [x] Fields match schema column names
- [x] `from_dict` builds from dict following schema (lines 47-50)
- [x] `as_form_data()` uses `FORM_FIELD_MAP` (line 52-54)
- [x] `from_xlsx(path)` returns `DataSource[dict]` (lines 57-60)
- [x] Uses generic `XlsxSource(path, RPA_CHALLENGE_SCHEMA)` (line 60)
- [x] `load_records` is side-effect free (lines 63-88)
- [x] Accepts any `DataSource` (line 64)
- [x] Applies predicate lazily (line 84)
- [x] Returns `list[ChallengeRecord]` or `list[dict]` based on `as_dataclass` flag

**Issues Found:**

1. **TODO (minor):** Unused import `iter_normalized_rows` (line 9)
   ```python
   from .data.sources.html import iter_normalized_rows
   ```
   - This import isn't used in the file
   - **Recommendation:** Remove unused import

**PASS with minor cleanup needed.**

---

### 3.3 Legacy Facade: `downloads.py`

**File:** `src/cpmf_rpachallenge/downloads.py`

**Checks:**

- [x] Module marked as DEPRECATED in docstring (lines 1-4)
- [x] Imports from new modules (lines 13-14):
  ```python
  from .fetch import fetch_challenge_excel
  from .records import ChallengeRecord, from_xlsx, load_records
  ```
- [x] `Downloads` class marked DEPRECATED (line 23)
- [x] `fetch_excel` delegates to `fetch_challenge_excel` (line 46)
- [x] `fetch_excel_async` delegates to `fetch_challenge_excel_async` (lines 59-61)
- [x] `read_challenge_data` uses `from_xlsx` + `load_records` (lines 74-76)
- [x] `get_challenge_data` uses same pattern (lines 88-89)
- [x] All methods emit `DeprecationWarning` (lines 41-44, 54-57, 69-72, 83-86)
- [x] No duplicate `ChallengeRecord` definition
- [x] No `openpyxl` parsing logic

**PASS** - Clean legacy facade with proper deprecation warnings.

---

## 4. Validation Layer Alignment

**File:** `src/cpmf_rpachallenge/validation.py`

**Checks:**

- [x] Import changed from `.downloads` to `.records` (line 13):
  ```python
  from .records import ChallengeRecord
  ```
- [x] All validation logic is pure (no IO, HTTP, or config access)
- [x] `EXPECTED_RECORD_COUNT = 10` (line 99)

**PASS** - No issues found.

---

## 5. Results Parsing

**File:** `src/cpmf_rpachallenge/results.py`

**Checks:**

- [x] `Results.parse_results(message2_text)` is pure (lines 18-40)
- [x] Regex matches expected text structure (lines 28-30)
- [x] Fallback returns `ResultData(raw_message=message2_text)` (line 40)
- [x] `ResultData` default values make sense (lines 45-51)
- [x] `fields_incorrect` property correct (lines 54-55)
- [x] `time_seconds` property correct (lines 57-58)

**PASS** - No changes required.

---

## 6. Top-level API (`__init__.py`)

**File:** `src/cpmf_rpachallenge/__init__.py`

**Checks:**

- [x] Exports dual API (lines 72-112):
  - **Procedural (new):** `fetch_challenge_excel`, `fetch_challenge_excel_async`
  - **Functional (new):** `from_xlsx`, `load_records`, `ChallengeRecord`, `RPA_CHALLENGE_SCHEMA`, `FORM_FIELD_MAP`
  - **Legacy (deprecated):** `Downloads`
- [x] Client API added: `RPAChallengeClient`, `Backend`, `PlaywrightBackend`
- [x] Docstring documents both APIs (lines 14-22)

**Issues Found:**

1. **TODO:** Missing exports from `data/` layer:
   - `DataSource`, `Column`, `Schema`, `filter_records`, `map_records`, `collect` not exported
   - Users cannot access generic data abstractions directly
   - **Recommendation:** Add to `__all__`:
     ```python
     from .data import DataSource, Column, Schema, filter_records, map_records, collect
     ```

**PASS with enhancement opportunity.**

---

## 7. Consistency & Tests

### Domain Leakage Check

**TODO:** Verify no file under `data/` imports domain modules:

```bash
grep -r "from.*config\|from.*downloads\|from.*records\|from.*results\|from.*fetch" src/cpmf_rpachallenge/data/
```

**Found Issue:**
- `data/sources/html.py` imports `playwright` - this is a driver dependency that shouldn't be in the generic data layer

### Current Test Coverage

| File | Tests | Notes |
|------|-------|-------|
| `test_forms.py` | 4 tests | Selector existence |
| `test_validation.py` | 6 tests | Validation logic |

### Proposed Additional Tests

**Procedural path:**
- [ ] `test_fetch_challenge_excel()`: Returns valid Path to .xlsx
- [ ] `test_downloads_deprecated()`: Verify DeprecationWarning is emitted

**Functional path:**
- [ ] `test_functional_path_equivalence()`:
  ```python
  import warnings
  with warnings.catch_warnings():
      warnings.simplefilter("ignore", DeprecationWarning)
      legacy = Downloads.get_challenge_data()

  path = fetch_challenge_excel()
  source = from_xlsx(path)
  functional = load_records(source, as_dataclass=True)

  assert len(functional) == len(legacy) == 10
  for f, l in zip(functional, legacy):
      assert f.first_name == l.first_name
      # ... etc
  ```

- [ ] `test_load_records_with_predicate()`:
  ```python
  records = load_records(source, predicate=lambda r: "Manager" in r["role"])
  assert all("Manager" in r.role for r in records)
  ```

- [ ] `test_load_records_as_dict()`:
  ```python
  records = load_records(source, as_dataclass=False)
  assert all(isinstance(r, dict) for r in records)
  ```

---

## 8. Additional Findings

### 8.1 Client Architecture

**Files:** `client.py`, `backends/protocol.py`, `backends/playwright.py`

The codebase includes a client/backend architecture that wasn't in the original review brief but is well-designed:

- `RPAChallengeClient` - domain-facing API (backend-agnostic)
- `Backend` - protocol for driver implementations
- `PlaywrightBackend` - Playwright-specific implementation

**Issue Found in `client.py` (line 10):**
```python
from .downloads import ChallengeRecord, Downloads
```
- Imports `Downloads` (deprecated) instead of using new API
- `get_records()` method (line 60) calls deprecated `Downloads.get_challenge_data()`

**TODO:** Update `client.py`:
```python
from .records import ChallengeRecord
from .fetch import fetch_challenge_excel
from .records import from_xlsx, load_records

def get_records(self) -> list[ChallengeRecord]:
    path = fetch_challenge_excel()
    return load_records(from_xlsx(path))
```

**Issue Found in `backends/protocol.py` (line 11):**
```python
from ..downloads import ChallengeRecord
```
- Should import from `.records` instead

---

## 9. Action Items Summary

### Critical (Architecture Violations)

| File | Issue | Action |
|------|-------|--------|
| `data/sources/html.py` | Playwright import in generic layer | Move to `backends/` or `playwright_utils.py` |

### High Priority (Code Quality)

| File | Issue | Action |
|------|-------|--------|
| `client.py:10` | Imports from deprecated `downloads` | Change to import from `records` + `fetch` |
| `client.py:60` | Uses deprecated `Downloads.get_challenge_data()` | Use new API |
| `backends/protocol.py:11` | Imports from deprecated `downloads` | Change to `from ..records import ChallengeRecord` |
| `records.py:9` | Unused import `iter_normalized_rows` | Remove |

### Medium Priority (Enhancements)

| File | Issue | Action |
|------|-------|--------|
| `__init__.py` | Missing generic data layer exports | Add `DataSource`, `Column`, etc. to `__all__` |
| `data/protocol.py` | Combinators return `Iterable`, not `DataSource` | Consider wrapper for composability (optional) |

### Low Priority (Tests/Docs)

| Item | Action |
|------|--------|
| Tests | Add functional path tests |
| Tests | Add deprecation warning tests |
| README | Add dual API examples (procedural vs functional) |

---

## 10. Checklist Summary

### Data Layer
- [x] `data/__init__.py` exports only generic abstractions
- [x] `DataSource` Protocol with `load() -> Iterable[T]`
- [x] `Column` frozen dataclass with `parse()` method
- [x] `filter_records`, `map_records` lazy (return generators)
- [x] `XlsxSource` is domain-agnostic
- [ ] **FAIL:** `sources/html.py` has Playwright dependency

### Procedural/Functional Split
- [x] `fetch.py` contains ONLY HTTP + filesystem operations
- [x] `records.py` contains ONLY schema + parsing logic
- [x] `downloads.py` delegates to new modules with deprecation warnings
- [x] No parsing in fetch, no IO in records

### Validation
- [x] Import `ChallengeRecord` from `.records`
- [x] All validation logic remains pure

### API
- [x] Procedural exports preserved for backwards compatibility
- [x] Functional exports added for composability
- [ ] Generic abstractions not fully exported (minor)

### Consistency
- [ ] `client.py` and `backends/protocol.py` still use deprecated imports

---

*End of Review*
