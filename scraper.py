from playwright.sync_api import sync_playwright

email = "gfz5au@email.com"
password = "Drjie_5004!!"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://www.gradescope.com")

    # Fill in the login form
    page.fill('input[name="session[email]"]', email)
    page.fill('input[name="session[password]"]', password)
    page.click('input[type="submit"]')

    # Wait for the dashboard to load
    page.wait_for_load_state("networkidle")

    print(page.title())

    input("Press Enter to close...")
    browser.close()
