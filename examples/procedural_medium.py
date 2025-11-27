"""Procedural approach - MEDIUM (moderate abstraction).

Shows explicit control over workflow steps with client convenience methods.
"""

import asyncio
from playwright.async_api import async_playwright
from cpmf_rpachallenge.procedural import RPAChallengeClient
from cpmf_rpachallenge.backends import PlaywrightBackend


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://rpachallenge.com")

        backend = PlaywrightBackend(page)
        client = RPAChallengeClient(backend=backend)

        # Medium - explicit workflow with validation
        records = client.get_records()
        validation = client.validate_records(records)

        if not validation.is_valid:
            print(f"[WARN] Data validation failed: {validation.summary}")
            return

        await client.start_async()

        for i, record in enumerate(records, 1):
            await client.fill_form_async(record)
            await client.submit_async()
            print(f"[OK] Submitted record {i}/{len(records)}")

        result = await client.get_result_async()
        print(f"[OK] Success: {result.success_rate}% in {result.time_ms}ms")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
