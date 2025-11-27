# Side-by-Side Comparison

## MINIMAL - Maximum Convenience

### Procedural (13 lines)
```python
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://rpachallenge.com")

        # ONE LINE DOES EVERYTHING
        backend = PlaywrightBackend(page)
        client = RPAChallengeClient(backend=backend)
        result = await client.run_async()

        print(f"✓ Success: {result.success_rate}% in {result.time_ms}ms")
        await browser.close()
```

**Key**: `client.run_async()` - single method handles data + automation

### Functional (25 lines)
```python
async def main():
    # COMPOSABLE PIPELINE
    source = from_xlsx(fetch_challenge_excel())
    filtered = filter_records(source, lambda r: len(r.get("email", "")) > 0)
    records = load_records(filtered)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://rpachallenge.com")

        await page.click(Pages.ChallengePage.Buttons.START)

        for record in records:
            for field, value in record.as_form_data().items():
                await page.fill(f'input[ng-reflect-name="{field}"]', value)
            await page.click(Pages.ChallengePage.Buttons.SUBMIT)

        message = await page.inner_text(Pages.ChallengePage.Results.MESSAGE_DETAILS)
        result = Results.parse_results(message)
        print(f"✓ Success: {result.success_rate}% in {result.time_seconds}s")
        await browser.close()
```

**Key**: Explicit data pipeline, Playwright automation visible

---

## MEDIUM - Moderate Control

### Procedural (32 lines)
```python
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://rpachallenge.com")

        backend = PlaywrightBackend(page)
        client = RPAChallengeClient(backend=backend)

        # EXPLICIT WORKFLOW STEPS
        records = client.get_records()
        validation = client.validate_records(records)

        if not validation.is_valid:
            print(f"⚠ Data validation failed: {validation.summary}")
            return

        await client.start_async()

        for i, record in enumerate(records, 1):
            await client.fill_form_async(record)
            await client.submit_async()
            print(f"✓ Submitted record {i}/{len(records)}")

        result = await client.get_result_async()
        print(f"✓ Success: {result.success_rate}% in {result.time_ms}ms")
        await browser.close()
```

**Key**: Client convenience methods but YOU control flow

### Functional (37 lines)
```python
async def main():
    # EXPLICIT SOURCE CONSTRUCTION
    path = fetch_challenge_excel()
    source = XlsxSource(path, RPA_CHALLENGE_SCHEMA, header_map=EXCEL_HEADER_MAP)

    # PURE TRANSFORMATIONS
    dicts = collect(source)
    records = [ChallengeRecord.from_dict(d) for d in dicts]

    # PURE VALIDATION
    valid_records = [r for r in records if r.email and "@" in r.email]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://rpachallenge.com")

        await page.click(Pages.ChallengePage.Buttons.START)

        for i, record in enumerate(valid_records, 1):
            form_data = record.as_form_data()
            for field, value in form_data.items():
                await page.fill(f'input[ng-reflect-name="{field}"]', value)
            await page.click(Pages.ChallengePage.Buttons.SUBMIT)
            print(f"✓ Record {i}/{len(valid_records)}")

        message = await page.inner_text(Pages.ChallengePage.Results.MESSAGE_DETAILS)
        result = Results.parse_results(message)
        print(f"✓ Success: {result.success_rate}%")
        await browser.close()
```

**Key**: Explicit source + pure transformations

---

## VERBOSE - Maximum Control

### Procedural (30 lines)
```python
async def main():
    # EXPLICIT DATA LOADING
    path = fetch_challenge_excel()
    records = load_records(from_xlsx(path))

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://rpachallenge.com")

        # DIRECT BACKEND CALLS (no client wrapper)
        backend = PlaywrightBackend(page)

        await backend.start_async()

        for i, record in enumerate(records, 1):
            await backend.fill_form_async(record)
            await backend.submit_async()
            print(f"✓ Form {i}/{len(records)}")

        result = await backend.get_result_async()
        print(f"✓ {result.success_rate}% in {result.time_ms}ms")
        await browser.close()
```

**Key**: No client wrapper - direct backend access

### Functional (28 lines)
```python
async def main():
    # RAW SOURCE ITERATION
    source = XlsxSource(fetch_challenge_excel(), RPA_CHALLENGE_SCHEMA, header_map=EXCEL_HEADER_MAP)

    async with async_playwright() as p:
        page = await (await p.chromium.launch(headless=False)).new_page()
        await page.goto("https://rpachallenge.com")
        await page.click(Pages.ChallengePage.Buttons.START)

        # MANUAL FIELD MAPPING
        for i, record in enumerate(source.load(), 1):
            for schema_field, ng_name in FORM_FIELD_MAP.items():
                value = str(record.get(schema_field, ""))
                await page.fill(f'input[ng-reflect-name="{ng_name}"]', value)
            await page.click(Pages.ChallengePage.Buttons.SUBMIT)
            print(f"✓ {i}")

        # RAW RESULT PARSING
        msg = await page.inner_text(Pages.ChallengePage.Results.MESSAGE_DETAILS)
        print(f"✓ Result: {msg.split()[4]}")
        await page.context.browser.close()
```

**Key**: Raw source iteration + manual field mapping

---

## Visual Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    ABSTRACTION LADDER                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  MINIMAL    ▲  Procedural: client.run_async()              │
│             │  Functional: helper chains                    │
│             │  → Maximum convenience                        │
│             │                                               │
│  MEDIUM     │  Procedural: client methods                  │
│             │  Functional: explicit sources                │
│             │  → Balanced control                           │
│             │                                               │
│  VERBOSE    │  Procedural: direct backend                  │
│             ▼  Functional: raw iteration                    │
│                → Maximum control                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Key Insights

### When Code Length Matters
- **Shortest**: Procedural Minimal (13 lines)
- **Most explicit**: Functional Medium (37 lines)
- **Most balanced**: Functional Verbose (28 lines)

### Abstraction Trade-offs

| Level | Convenience | Control | Testability | Learning Curve |
|-------|-------------|---------|-------------|----------------|
| Minimal | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ | Easy |
| Medium | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | Moderate |
| Verbose | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Advanced |

### Paradigm Strengths

**Procedural Wins**:
- ✓ Brevity at high abstraction levels
- ✓ Familiar to most developers
- ✓ Natural for imperative workflows
- ✓ Stateful workflow management

**Functional Wins**:
- ✓ Composable data pipelines
- ✓ Testable transformations
- ✓ Clear separation of I/O and logic
- ✓ Reusable data sources
