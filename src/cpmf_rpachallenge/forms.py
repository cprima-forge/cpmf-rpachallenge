"""Form field selectors for rpachallenge.com

⚠️ DEPRECATED - This module is deprecated and will be removed in a future version.

Use the Page Object pattern from domain.selectors instead:

    Old (deprecated):
        from cpmf_rpachallenge import FormFields, Buttons
        page.fill(FormFields.FIRST_NAME, "John")
        page.click(Buttons.START)

    New (recommended):
        from cpmf_rpachallenge.domain.selectors import Pages
        page.fill(Pages.ChallengePage.Fields.FIRST_NAME, "John")
        page.click(Pages.ChallengePage.Buttons.START)

This module is kept for backwards compatibility only.
"""

import warnings

from .domain.selectors import Pages

# Issue deprecation warning on import
warnings.warn(
    "forms.py is deprecated. Use 'from cpmf_rpachallenge.domain.selectors import Pages' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Backwards compatibility aliases - DEPRECATED
FormFields = Pages.ChallengePage.Fields
Buttons = Pages.ChallengePage.Buttons

__all__ = ["FormFields", "Buttons", "Pages"]
