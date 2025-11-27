"""Generic Excel file source - schema-driven parsing.

Generic - no domain-specific imports.
"""

from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

import openpyxl

from ..schema import Schema

RowToDict = Callable[[tuple, Schema], Mapping[str, Any]]


def default_row_to_dict(row: tuple, schema: Schema) -> dict[str, Any]:
    """Default row parser using schema."""
    return {
        col.name: col.parse(row[i]) for i, col in enumerate(schema) if i < len(row)
    }


class XlsxSource:
    """Generic Excel file source - schema-driven parsing."""

    def __init__(
        self,
        path: Path | str,
        schema: Schema,
        row_to_dict: RowToDict = default_row_to_dict,
        *,
        data_start_row: int = 2,
    ):
        self.path = Path(path)
        self.schema = schema
        self.row_to_dict = row_to_dict
        self.data_start_row = data_start_row

    def load(self) -> Iterable[dict[str, Any]]:
        """Yield records from Excel file."""
        wb = openpyxl.load_workbook(self.path)
        sheet = wb.active
        for row in sheet.iter_rows(min_row=self.data_start_row, values_only=True):
            if row[0] is None:  # Skip empty rows
                continue
            yield self.row_to_dict(row, self.schema)
