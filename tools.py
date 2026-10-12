import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
BASE_URL = os.getenv("STARX_BASE_URL", "http://127.0.0.1:8000")

def submit_approval_via_browser(expense_id: str):
    """Navigate the company UI and click Submit for Approval."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(f"{BASE_URL}/", wait_until="domcontentloaded")
            page.get_by_role(page.get_by_role("link",name="Expenses",exact=True).click())
            page.get_by_label("Employee name").fill("Rahul Sharma")
            page.get_by_role("button", name="Search").click()
            page.get_by_role("link", name=f"Open {expense_id}").click()
            button = page.get_by_role("button", name="Submit for Approval")
            if button.count() == 0:
                return {"expense_id": expense_id, "status": page.locator("#expense-status").inner_text(),
                        "message": "Already submitted or awaiting approval"}
            button.click()
            page.wait_for_url(f"**/expenses/{expense_id}")
            page.get_by_text("Approval request submitted").wait_for(timeout=5000)
            return {"expense_id": expense_id, "status": page.locator("#expense-status").inner_text(),
                    "message": "Approval request submitted"}
        except PlaywrightTimeoutError as exc:
            raise RuntimeError(f"Timed out in browser UI: {exc}") from exc
        finally:
            browser.close()

def verify_via_browser(expense_id: str):
    """Reopen the expense page in a fresh browser and verify the rendered state."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(f"{BASE_URL}/expenses/{expense_id}", wait_until="domcontentloaded")
            return {"expense_id": expense_id, "status": page.locator("#expense-status").inner_text(),
                    "message": page.locator("#confirmation").inner_text()}
        finally:
            browser.close()
