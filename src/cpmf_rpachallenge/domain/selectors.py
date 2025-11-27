"""Page Object selectors for rpachallenge.com clone.

Organizes selectors by page/component for multi-page webapps.

Architecture:
    Pages.ChallengePage - Main form page (index.html)
    Pages.DataTablePage - Paginated data tables (data/page*.html)

Migration:
    Old: from cpmf_rpachallenge.forms import FormFields
    New: from cpmf_rpachallenge import Pages
         Pages.ChallengePage.Fields.FIRST_NAME
"""


class Pages:
    """Page Object container for all pages."""

    class ChallengePage:
        """Main challenge form page (index.html)."""

        # Page-level selectors
        FORM = "form#challengeForm"
        CONGRATULATIONS = "div.congratulations"

        class Fields:
            """Form input fields."""

            FIRST_NAME = 'input[ng-reflect-name="labelFirstName"]'
            LAST_NAME = 'input[ng-reflect-name="labelLastName"]'
            PHONE = 'input[ng-reflect-name="labelPhone"]'
            EMAIL = 'input[ng-reflect-name="labelEmail"]'
            ADDRESS = 'input[ng-reflect-name="labelAddress"]'
            COMPANY_NAME = 'input[ng-reflect-name="labelCompanyName"]'
            ROLE = 'input[ng-reflect-name="labelRole"]'

            @classmethod
            def by_name(cls, ng_reflect_name: str) -> str:
                """Get field selector by ng-reflect-name.

                Args:
                    ng_reflect_name: Angular ng-reflect-name value (e.g., "labelFirstName")

                Returns:
                    CSS selector for the field

                Example:
                    selector = Pages.ChallengePage.Fields.by_name("labelFirstName")
                    page.fill(selector, "John")
                """
                mapping = {
                    "labelFirstName": cls.FIRST_NAME,
                    "labelLastName": cls.LAST_NAME,
                    "labelPhone": cls.PHONE,
                    "labelEmail": cls.EMAIL,
                    "labelAddress": cls.ADDRESS,
                    "labelCompanyName": cls.COMPANY_NAME,
                    "labelRole": cls.ROLE,
                }
                return mapping[ng_reflect_name]

        class Buttons:
            """Action buttons."""

            START = "button.uiColorButton"
            SUBMIT = 'input[type="submit"]'
            RESET = "button.uiColorButton"  # Text changes to RESET after start

        class Results:
            """Result display elements."""

            MESSAGE_CONTAINER = "div.congratulations"
            MESSAGE_TITLE = "div.message1"
            MESSAGE_DETAILS = "div.message2"

    class DataTablePage:
        """Paginated data table pages (data/page1-4.html)."""

        # Table selectors
        TABLE = "table.data-table"
        HEADERS = "thead tr th"
        ROWS = "tbody tr"
        CELLS = "tbody tr td"

        class Navigation:
            """Pagination navigation.

            Primary selector strategy: Element type distinction
            - Active links: <a> elements (clickable)
            - Disabled state: <span> elements (non-clickable)

            Alternative strategies provided for testing flexibility.
            """

            # Element type-based selectors (primary strategy)
            FIRST = "a[data-nav='first']"  # Active first button
            FIRST_DISABLED = "span[data-nav='first']"  # Disabled first button

            PREV = "a[data-nav='prev']"  # Active previous button
            PREV_DISABLED = "span[data-nav='prev']"  # Disabled previous button

            NEXT = "a[data-nav='next']"  # Active next button
            NEXT_DISABLED = "span[data-nav='next']"  # Disabled next button

            LAST = "a[data-nav='last']"  # Active last button
            LAST_DISABLED = "span[data-nav='last']"  # Disabled last button

            # Attribute-based selectors (fallback - matches both states)
            ANY_FIRST = "[data-nav='first']"
            ANY_PREV = "[data-nav='prev']"
            ANY_NEXT = "[data-nav='next']"
            ANY_LAST = "[data-nav='last']"

            # Class-based selectors (alternative strategy)
            FIRST_CLASS_DISABLED = ".nav-item.disabled[data-nav='first']"
            PREV_CLASS_DISABLED = ".nav-item.disabled[data-nav='prev']"
            NEXT_CLASS_DISABLED = ".nav-item.disabled[data-nav='next']"
            LAST_CLASS_DISABLED = ".nav-item.disabled[data-nav='last']"

            # Page info
            PAGE_INFO = "span.page-info"
