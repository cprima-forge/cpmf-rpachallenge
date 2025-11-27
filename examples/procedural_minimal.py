"""Procedural approach - MINIMAL (highest abstraction).

Shows maximum convenience - single method call handles everything.
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

        # Minimal - single line does everything
        backend = PlaywrightBackend(page)
        client = RPAChallengeClient(backend=backend)
        result = await client.run_async()

        print(f"[OK] Success: {result.success_rate}% in {result.time_ms}ms")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
