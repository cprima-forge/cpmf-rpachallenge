"""Tests for data validation."""

# Modern API - import from domain
from cpmf_rpachallenge.domain import ChallengeRecord, DataValidator


def test_valid_record():
    """Test validation of a valid record."""
    record = ChallengeRecord(
        first_name="John",
        last_name="Doe",
        company_name="Acme Corp",
        role="Developer",
        address="123 Main St",
        email="john@example.com",
        phone="1234567890",
    )
    result = DataValidator.validate_record(record)
    assert result.is_valid
    assert result.error_count == 0


def test_invalid_email():
    """Test validation catches invalid email."""
    record = ChallengeRecord(
        first_name="John",
        last_name="Doe",
        company_name="Acme Corp",
        role="Developer",
        address="123 Main St",
        email="invalid-email",
        phone="1234567890",
    )
    result = DataValidator.validate_record(record)
    assert not result.is_valid
    assert any(e.field == "email" for e in result.errors)


def test_empty_required_field():
    """Test validation catches empty required fields."""
    record = ChallengeRecord(
        first_name="",
        last_name="Doe",
        company_name="Acme Corp",
        role="Developer",
        address="123 Main St",
        email="john@example.com",
        phone="1234567890",
    )
    result = DataValidator.validate_record(record)
    assert not result.is_valid
    assert any(e.field == "first_name" for e in result.errors)


def test_short_phone():
    """Test validation catches short phone numbers."""
    record = ChallengeRecord(
        first_name="John",
        last_name="Doe",
        company_name="Acme Corp",
        role="Developer",
        address="123 Main St",
        email="john@example.com",
        phone="123",
    )
    result = DataValidator.validate_record(record)
    assert not result.is_valid
    assert any(e.field == "phone" for e in result.errors)


def test_validate_multiple_records():
    """Test validation of multiple records."""
    records = [
        ChallengeRecord(
            first_name="John",
            last_name="Doe",
            company_name="Acme",
            role="Dev",
            address="123 St",
            email="john@test.com",
            phone="1234567890",
        )
        for _ in range(10)
    ]
    result = DataValidator.validate(records)
    assert result.is_valid
    assert result.record_count == 10
    assert result.valid_count == 10


def test_wrong_record_count():
    """Test validation catches wrong record count."""
    records = [
        ChallengeRecord(
            first_name="John",
            last_name="Doe",
            company_name="Acme",
            role="Dev",
            address="123 St",
            email="john@test.com",
            phone="1234567890",
        )
        for _ in range(5)
    ]
    result = DataValidator.validate(records, expected_count=10)
    assert not result.is_valid
    assert result.record_count == 5
    assert result.expected_count == 10
