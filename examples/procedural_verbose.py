"""Procedural approach - VERBOSE (lowest abstraction, max 30 lines).

Shows direct backend usage without client wrapper - explicit control.
"""

import asyncio
from playwright.async_api import async_playwright
from cpmf_rpachallenge.backends import PlaywrightBackend
from cpmf_rpachallenge import fetch_challenge_excel
from cpmf_rpachallenge.domain import from_xlsx, load_records


async def main():
    path = fetch_challenge_excel()
    records = load_records(from_xlsx(path))

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://rpachallenge.com")

        backend = PlaywrightBackend(page)

        # Verbose - direct backend calls, no client
        await backend.start_async()

        for i, record in enumerate(records, 1):
            await backend.fill_form_async(record)
            await backend.submit_async()
            print(f"[OK] Form {i}/{len(records)}")

        result = await backend.get_result_async()
        print(f"[OK] {result.success_rate}% in {result.time_ms}ms")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
