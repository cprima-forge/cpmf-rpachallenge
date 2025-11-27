"""Functional approach - MINIMAL (highest abstraction).

Shows composable data pipelines with helper functions.
"""

import asyncio
from playwright.async_api import async_playwright
from cpmf_rpachallenge import fetch_challenge_excel
from cpmf_rpachallenge.domain import from_xlsx, load_records, Results
from cpmf_rpachallenge.domain.selectors import Pages
from cpmf_rpachallenge.functional import filter_records


async def main():
    # Functional pipeline - composable transformations
    source = from_xlsx(fetch_challenge_excel())
    filtered = filter_records(source, lambda r: len(r.get("email", "")) > 0)
    records = load_records(filtered)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://rpachallenge.com")

        await page.click(Pages.ChallengePage.Buttons.START)

        for record in records:
            for field, value in record.as_form_data().items():
                await page.fill(f'input[ng-reflect-name="{field}"]', value)
            await page.click(Pages.ChallengePage.Buttons.SUBMIT)

        message = await page.inner_text(Pages.ChallengePage.Results.MESSAGE_DETAILS)
        result = Results.parse_results(message)
        print(f"[OK] Success: {result.success_rate}% in {result.time_seconds}s")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
