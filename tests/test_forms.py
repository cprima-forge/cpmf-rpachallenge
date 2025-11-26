"""Tests for form selectors."""

from cpmf_rpachallenge import FormFields, Buttons


def test_form_field_selectors_exist():
    """Test that all form field selectors are defined."""
    assert FormFields.FIRST_NAME
    assert FormFields.LAST_NAME
    assert FormFields.PHONE
    assert FormFields.EMAIL
    assert FormFields.ADDRESS
    assert FormFields.COMPANY_NAME
    assert FormFields.ROLE


def test_form_field_selectors_use_ng_reflect_name():
    """Test that selectors use ng-reflect-name attribute."""
    assert 'ng-reflect-name="labelFirstName"' in FormFields.FIRST_NAME
    assert 'ng-reflect-name="labelLastName"' in FormFields.LAST_NAME
    assert 'ng-reflect-name="labelEmail"' in FormFields.EMAIL


def test_by_name_method():
    """Test the by_name helper method."""
    assert FormFields.by_name("labelFirstName") == FormFields.FIRST_NAME
    assert FormFields.by_name("labelEmail") == FormFields.EMAIL


def test_button_selectors_exist():
    """Test that button selectors are defined."""
    assert Buttons.START
    assert Buttons.SUBMIT
    assert Buttons.RESET
