from typing import Any, Callable, Iterable

from playwright.sync_api import Locator, Page

from ..schema import Schema


def iter_normalized_rows(
    page: Page,
    *,
    table_selector: str,
    row_selector: str,
    schema: Schema,
    row_filter: Callable[[dict[str, Any]], bool] | None = None,
) -> Iterable[dict[str, Any]]:
    table: Locator = page.locator(table_selector)
    table.wait_for()
    rows = table.locator(row_selector)
    expected = len(schema)

    for i in range(rows.count()):
        row = rows.nth(i)
        cells = row.locator("td")
        vals = [cells.nth(j).inner_text() if j < cells.count() else None for j in range(expected)]
        rec = {col.name: col.parse(vals[k]) for k, col in enumerate(schema)}
        if row_filter is None or row_filter(rec):
            yield rec
