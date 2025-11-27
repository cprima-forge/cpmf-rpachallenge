# RPAChallenge Examples - Paradigm Comparison

This directory demonstrates solving the rpachallenge.com automation using **two paradigms** at **three abstraction levels**.

## Overview

| Paradigm | Minimal | Medium | Verbose |
|----------|---------|--------|---------|
| **Procedural** | Client with `.run()` | Client with explicit steps | Direct backend calls |
| **Functional** | Composable pipelines | Explicit sources | Manual iteration |

## Files

### Procedural Paradigm

**Philosophy**: Imperative, step-by-step workflows with mutable state.

1. **`procedural_minimal.py`** (13 lines) - **Highest convenience**
   - Single method call: `client.run_async()`
   - Client handles everything: fetch data, validation, automation
   - **Use when**: You want maximum convenience and don't need custom logic

2. **`procedural_medium.py`** (32 lines) - **Moderate control**
   - Explicit workflow: `get_records()` → `validate()` → `start()` → loop → `get_result()`
   - Client provides convenience methods but you control flow
   - **Use when**: You need custom logic between steps (logging, error handling, filtering)

3. **`procedural_verbose.py`** (30 lines) - **Maximum control**
   - Direct backend usage without client wrapper
   - Explicit data loading and backend interaction
   - **Use when**: You need full control or are building your own client

### Functional Paradigm

**Philosophy**: Pure transformations, composable data sources, immutable pipelines.

1. **`functional_minimal.py`** (25 lines) - **Highest abstraction**
   - Composable pipeline: `from_xlsx()` → `filter_records()` → `load_records()`
   - Declarative data flow with helper functions
   - **Use when**: You want clean, composable data transformations

2. **`functional_medium.py`** (37 lines) - **Explicit sources**
   - Manual source construction: `XlsxSource(path, schema, header_map)`
   - Explicit transformations: `collect()`, list comprehensions
   - Pure functions for validation
   - **Use when**: You need fine-grained control over data sources

3. **`functional_verbose.py`** (28 lines) - **Low-level control**
   - Direct source iteration: `for record in source.load()`
   - Manual field mapping using schema constants
   - No helper functions
   - **Use when**: You need maximum control or are building custom sources

## Key Contrasts

### Abstraction Levels

```
MINIMAL (High Abstraction)
↓ More convenience, less control
MEDIUM (Moderate Abstraction)
↓ More control, less convenience
VERBOSE (Low Abstraction)
```

### Procedural vs Functional

| Aspect | Procedural | Functional |
|--------|------------|------------|
| **Data Flow** | Imperative steps | Composable pipelines |
| **State** | Mutable (client holds state) | Immutable (pure transformations) |
| **Abstraction** | Object methods (`.run()`, `.get_records()`) | Functions and sources |
| **Error Handling** | Try/catch around client calls | Pure validation functions |
| **Testing** | Mock client/backend | Test pure functions, mock I/O |
| **Best For** | End-to-end automation scripts | Data processing, ETL, composition |

### Code Length

| Level | Procedural | Functional |
|-------|------------|------------|
| Minimal | 13 lines | 25 lines |
| Medium | 32 lines | 37 lines |
| Verbose | 30 lines | 28 lines |

*Note: Functional minimal is longer because it shows explicit Playwright automation. Procedural minimal hides this in the client.*

## Running Examples

```bash
# Install dependencies
uv pip install -e ".[playwright]"
playwright install chromium

# Run any example
python examples/procedural_minimal.py
python examples/functional_medium.py
```

## When to Use Each Approach

### Use Procedural When:
- ✓ You want maximum convenience (minimal)
- ✓ Building end-to-end automation scripts
- ✓ Team prefers object-oriented patterns
- ✓ Need stateful workflow management

### Use Functional When:
- ✓ Processing data from multiple sources
- ✓ Building composable pipelines
- ✓ Need testable, pure transformations
- ✓ Working in ETL/data engineering context
- ✓ Want to chain filters, maps, validations

### Hybrid Approach
You can mix both! Use functional for data processing and procedural for automation:

```python
# Functional - data processing
source = from_xlsx(path)
filtered = filter_records(source, my_predicate)
records = load_records(filtered)

# Procedural - automation
client = RPAChallengeClient(backend)
await client.start_async()
for record in records:
    await client.fill_form_async(record)
    await client.submit_async()
```

## Architecture Layers Used

Each example uses different layers:

- **Procedural Minimal**: `procedural/` → `backends/` → `domain/`
- **Procedural Medium**: `procedural/` → `backends/` → `domain/`
- **Procedural Verbose**: `backends/` → `domain/` (no procedural wrapper)
- **Functional Minimal**: `functional/` → `domain/` (helpers)
- **Functional Medium**: `functional/` (explicit sources) → `domain/`
- **Functional Verbose**: `functional/` (raw sources) → direct field mapping

## Educational Value

These examples demonstrate:

1. **Abstraction Spectrum**: From high-level convenience to low-level control
2. **Paradigm Contrast**: Imperative vs declarative, mutable vs immutable
3. **API Design**: How to layer abstractions for different use cases
4. **Practical Trade-offs**: Convenience vs control, brevity vs explicitness
