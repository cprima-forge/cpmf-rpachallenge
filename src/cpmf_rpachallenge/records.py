"""RPAChallenge domain: schema, record type, and factory functions."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

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


# One-line factory - keeps XlsxSource generic
def from_xlsx(path: Path | str) -> DataSource[dict]:
    """Create data source from Excel file path."""
    return XlsxSource(path, RPA_CHALLENGE_SCHEMA)


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
