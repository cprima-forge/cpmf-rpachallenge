"""Functional approach - MEDIUM (moderate abstraction).

Shows explicit source construction with pure transformations.
"""

import asyncio
from playwright.async_api import async_playwright
from cpmf_rpachallenge import fetch_challenge_excel
from cpmf_rpachallenge.domain import (
    ChallengeRecord,
    RPA_CHALLENGE_SCHEMA,
    EXCEL_HEADER_MAP,
    Results,
)
from cpmf_rpachallenge.domain.selectors import Pages
from cpmf_rpachallenge.functional import XlsxSource, collect


async def main():
    # Medium - explicit source construction
    path = fetch_challenge_excel()
    source = XlsxSource(path, RPA_CHALLENGE_SCHEMA, header_map=EXCEL_HEADER_MAP)

    # Pure transformation - collect into domain objects
    dicts = collect(source)
    records = [ChallengeRecord.from_dict(d) for d in dicts]

    # Validation as pure function
    valid_records = [r for r in records if r.email and "@" in r.email]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://rpachallenge.com")

        await page.click(Pages.ChallengePage.Buttons.START)

        for i, record in enumerate(valid_records, 1):
            form_data = record.as_form_data()
            for field, value in form_data.items():
                await page.fill(f'input[ng-reflect-name="{field}"]', value)
            await page.click(Pages.ChallengePage.Buttons.SUBMIT)
            print(f"[OK] Record {i}/{len(valid_records)}")

        message = await page.inner_text(Pages.ChallengePage.Results.MESSAGE_DETAILS)
        result = Results.parse_results(message)
        print(f"[OK] Success: {result.success_rate}%")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
