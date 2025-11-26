"""Validation utilities for rpachallenge.com Excel data.

Validates ChallengeRecord data before automation to enable robust decision-making.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .downloads import ChallengeRecord


@dataclass
class FieldError:
    """Error for a specific field in a record."""

    field: str
    value: str
    message: str


@dataclass
class RecordValidationResult:
    """Validation result for a single record."""

    index: int
    is_valid: bool
    errors: list[FieldError] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def summary(self) -> str:
        if self.is_valid:
            return f"Record {self.index}: valid"
        error_fields = ", ".join(e.field for e in self.errors)
        return f"Record {self.index}: {self.error_count} error(s) in [{error_fields}]"


@dataclass
class DataValidationResult:
    """Validation result for all records."""

    is_valid: bool
    record_count: int
    expected_count: int
    records: list[RecordValidationResult] = field(default_factory=list)

    @property
    def valid_count(self) -> int:
        return sum(1 for r in self.records if r.is_valid)

    @property
    def invalid_count(self) -> int:
        return sum(1 for r in self.records if not r.is_valid)

    @property
    def invalid_records(self) -> list[RecordValidationResult]:
        return [r for r in self.records if not r.is_valid]

    @property
    def total_errors(self) -> int:
        return sum(r.error_count for r in self.records)

    @property
    def summary(self) -> str:
        if self.is_valid:
            return f"Valid: {self.record_count}/{self.expected_count} records, all fields OK"
        issues = []
        if self.record_count != self.expected_count:
            issues.append(f"expected {self.expected_count} records, got {self.record_count}")
        if self.invalid_count > 0:
            issues.append(f"{self.invalid_count} invalid record(s)")
        return f"Invalid: {', '.join(issues)}"


class DataValidator:
    """Validate ChallengeRecord data before automation.

    Usage:
        records = Downloads.get_challenge_data()
        result = DataValidator.validate(records)

        if not result.is_valid:
            print(f"Data issues: {result.summary}")
            for record in result.invalid_records:
                print(f"  {record.summary}")
                for error in record.errors:
                    print(f"    - {error.field}: {error.message}")
            # Decide whether to proceed or abort
    """

    # Expected number of records in challenge
    EXPECTED_RECORD_COUNT = 10

    # Simple email regex pattern
    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    # Required fields (cannot be empty)
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "company_name",
        "role",
        "address",
        "email",
        "phone",
    ]

    @classmethod
    def validate(
        cls,
        records: list[ChallengeRecord],
        expected_count: int | None = None,
    ) -> DataValidationResult:
        """Validate all records.

        Args:
            records: List of ChallengeRecord objects to validate.
            expected_count: Expected number of records. Defaults to 10.

        Returns:
            DataValidationResult with validation status and details.
        """
        if expected_count is None:
            expected_count = cls.EXPECTED_RECORD_COUNT

        record_results = []
        for i, record in enumerate(records):
            record_result = cls.validate_record(record, index=i)
            record_results.append(record_result)

        # Check overall validity
        all_records_valid = all(r.is_valid for r in record_results)
        count_valid = len(records) == expected_count
        is_valid = all_records_valid and count_valid

        return DataValidationResult(
            is_valid=is_valid,
            record_count=len(records),
            expected_count=expected_count,
            records=record_results,
        )

    @classmethod
    def validate_record(
        cls,
        record: ChallengeRecord,
        index: int = 0,
    ) -> RecordValidationResult:
        """Validate a single record.

        Args:
            record: ChallengeRecord to validate.
            index: Record index for error reporting.

        Returns:
            RecordValidationResult with validation status and errors.
        """
        errors: list[FieldError] = []

        # Check required fields
        for field_name in cls.REQUIRED_FIELDS:
            value = getattr(record, field_name, "")
            if not value or not str(value).strip():
                errors.append(
                    FieldError(
                        field=field_name,
                        value=str(value),
                        message="Field is required but empty",
                    )
                )

        # Validate email format
        if record.email and record.email.strip():
            if not cls.EMAIL_PATTERN.match(record.email.strip()):
                errors.append(
                    FieldError(
                        field="email",
                        value=record.email,
                        message=f"Invalid email format: '{record.email}'",
                    )
                )

        # Validate phone (should contain digits)
        if record.phone and record.phone.strip():
            digits = re.sub(r"\D", "", record.phone)
            if len(digits) < 7:
                errors.append(
                    FieldError(
                        field="phone",
                        value=record.phone,
                        message=f"Phone should have at least 7 digits, got {len(digits)}",
                    )
                )

        return RecordValidationResult(
            index=index,
            is_valid=len(errors) == 0,
            errors=errors,
        )

    @classmethod
    def is_valid(cls, records: list[ChallengeRecord]) -> bool:
        """Quick check if all records are valid.

        Args:
            records: List of ChallengeRecord objects.

        Returns:
            True if all records are valid, False otherwise.
        """
        return cls.validate(records).is_valid
