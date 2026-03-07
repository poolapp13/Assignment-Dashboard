from playwright.sync_api import sync_playwright
import json
import os

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    # Check if we already have a saved session
    if os.path.exists("session.json"):
        context = browser.new_context(storage_state="session.json")
        print("Loaded saved session")
    else:
        context = browser.new_context()

    page = context.new_page()
    page.goto("https://www.gradescope.com")

    # If not logged in, wait for you to log in manually
    if "dashboard" not in page.url:
        print("Please log in manually in the browser window...")
        # waits up to 2 minutes
        page.wait_for_url("**/dashboard**", timeout=120000)

        # Save the session so next time is automatic
        context.storage_state(path="session.json")
        print("Session saved!")

    print(page.title())
    input("Press Enter to close...")
    browser.close()
