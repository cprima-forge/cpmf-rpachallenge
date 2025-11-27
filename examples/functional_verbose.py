"""Functional approach - VERBOSE (lowest abstraction, max 30 lines).

Shows explicit source iteration and manual field extraction.
"""

import asyncio
from playwright.async_api import async_playwright
from cpmf_rpachallenge.functional import XlsxSource
from cpmf_rpachallenge.domain import RPA_CHALLENGE_SCHEMA, EXCEL_HEADER_MAP, FORM_FIELD_MAP
from cpmf_rpachallenge.domain.selectors import Pages
from cpmf_rpachallenge import fetch_challenge_excel


async def main():
    source = XlsxSource(fetch_challenge_excel(), RPA_CHALLENGE_SCHEMA, header_map=EXCEL_HEADER_MAP)

    async with async_playwright() as p:
        page = await (await p.chromium.launch(headless=False)).new_page()
        await page.goto("https://rpachallenge.com")
        await page.click(Pages.ChallengePage.Buttons.START)

        # Verbose - explicit iteration and field mapping
        for i, record in enumerate(source.load(), 1):
            for schema_field, ng_name in FORM_FIELD_MAP.items():
                value = str(record.get(schema_field, ""))
                await page.fill(f'input[ng-reflect-name="{ng_name}"]', value)
            await page.click(Pages.ChallengePage.Buttons.SUBMIT)
            print(f"[OK] {i}")

        msg = await page.inner_text(Pages.ChallengePage.Results.MESSAGE_DETAILS)
        print(f"[OK] Result: {msg.split()[4]}")
        await page.context.browser.close()


if __name__ == "__main__":
    asyncio.run(main())
