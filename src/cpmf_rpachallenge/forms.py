"""Form field selectors for rpachallenge.com

DEPRECATED: This module uses a flat selector structure. For better organization,
use the Page Object pattern instead:

    Old (deprecated):
        from cpmf_rpachallenge import FormFields, Buttons
        page.fill(FormFields.FIRST_NAME, "John")
        page.click(Buttons.START)

    New (recommended):
        from cpmf_rpachallenge import Pages
        page.fill(Pages.ChallengePage.Fields.FIRST_NAME, "John")
        page.click(Pages.ChallengePage.Buttons.START)

The form fields change position after each submission, but the
ng-reflect-name attribute remains stable and can be used to identify fields.

This module is kept for backwards compatibility only.
"""


class FormFields:
    """Input field selectors using stable ng-reflect-name attributes."""

    FIRST_NAME = 'input[ng-reflect-name="labelFirstName"]'
    LAST_NAME = 'input[ng-reflect-name="labelLastName"]'
    PHONE = 'input[ng-reflect-name="labelPhone"]'
    EMAIL = 'input[ng-reflect-name="labelEmail"]'
    ADDRESS = 'input[ng-reflect-name="labelAddress"]'
    COMPANY_NAME = 'input[ng-reflect-name="labelCompanyName"]'
    ROLE = 'input[ng-reflect-name="labelRole"]'

    # All fields as a dict for iteration
    ALL = {
        "first_name": FIRST_NAME,
        "last_name": LAST_NAME,
        "phone": PHONE,
        "email": EMAIL,
        "address": ADDRESS,
        "company_name": COMPANY_NAME,
        "role": ROLE,
    }

    # Mapping from ng-reflect-name values to selectors
    _BY_NAME = {
        "labelFirstName": FIRST_NAME,
        "labelLastName": LAST_NAME,
        "labelPhone": PHONE,
        "labelEmail": EMAIL,
        "labelAddress": ADDRESS,
        "labelCompanyName": COMPANY_NAME,
        "labelRole": ROLE,
    }

    # Mapping from Excel column names to selectors
    EXCEL_MAPPING = {
        "First Name": FIRST_NAME,
        "Last Name": LAST_NAME,
        "Phone Number": PHONE,
        "Email": EMAIL,
        "Address": ADDRESS,
        "Company Name": COMPANY_NAME,
        "Role in Company": ROLE,
    }

    @classmethod
    def by_name(cls, ng_reflect_name: str) -> str:
        """Get selector by ng-reflect-name value.

        Args:
            ng_reflect_name: The ng-reflect-name attribute value (e.g., "labelFirstName")

        Returns:
            CSS selector string for the input field.

        Raises:
            KeyError: If the ng-reflect-name is not recognized.
        """
        return cls._BY_NAME[ng_reflect_name]


class Buttons:
    """Button selectors."""

    START = "button.uiColorButton"
    SUBMIT = 'input[type="submit"]'
    RESET = "button.uiColorButton"  # Same as START, text changes to "RESET"
