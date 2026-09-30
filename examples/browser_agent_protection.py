# examples/browser_agent_protection.py

from playwright.sync_api import sync_playwright
from salamander import wear, UnsafeContentError

@wear(source="browser_page")
def fetch_page_content(url: str) -> str:
    """Fetch visible text from a webpage (protected)."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        content = page.inner_text("body")
        browser.close()
        return content


def safe_browse(url: str) -> str:
    try:
        envelope = fetch_page_content(url)
        return envelope.safe_content()
    except UnsafeContentError as e:
        print(f"🛡️ Blocked malicious page: {url}")
        print(f"Score: {e.result.score}")
        for f in e.result.findings:
            print(f"  - {f.category}: {f.matched_text[:80]}")
        return "[Content blocked by Salamander]"


if __name__ == "__main__":
    # صفحة عادية
    print(safe_browse("https://example.com")[:300])

    # صفحة تحتوي على حقن (يمكنك اختبارها محلياً)
    # print(safe_browse("https://your-test-page-with-injection.com"))
