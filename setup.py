from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import os

config = {}

print("=" * 50)
print("  ASSIGNMENT DASHBOARD SETUP")
print("=" * 50)

# Step 1: Canvas URL
canvas_url = input(
    "\nEnter your Canvas URL (e.g. canvas.university.edu): ").strip()
canvas_url = canvas_url.replace(
    "https://", "").replace("http://", "").rstrip("/")
config["canvas_url"] = canvas_url

with sync_playwright() as p:

    # ─── GRADESCOPE ───────────────────────────────────────
    print("\n[1/2] Setting up Gradescope...")
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.gradescope.com")
    input("    Log into Gradescope in the browser, then press Enter here...")
    context.storage_state(path="gradescope_session.json")
    print("    Session saved!")

    # Detect courses
    page.goto("https://www.gradescope.com")
    page.wait_for_load_state("networkidle")
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    course_boxes = soup.find_all("a", class_="courseBox")
    gs_courses = []
    for course in course_boxes:
        name_el = course.find("div", class_="courseBox--name")
        if name_el:
            gs_courses.append({
                "name": name_el.get_text(strip=True),
                "url": "https://www.gradescope.com" + course.get("href", "")
            })

    print("\n    Found these Gradescope courses:")
    for i, c in enumerate(gs_courses):
        print(f"      [{i}] {c['name']}")

    print("\n    Enter the numbers of courses to REMOVE (comma separated),")
    remove_input = input("    or just press Enter to keep all: ").strip()

    if remove_input:
        remove_indices = set(int(x.strip())
                             for x in remove_input.split(",") if x.strip().isdigit())
        gs_courses = [c for i, c in enumerate(
            gs_courses) if i not in remove_indices]

    config["gradescope_courses"] = gs_courses
    print(f"\n    Keeping {len(gs_courses)} Gradescope courses.")
    browser.close()

    # ─── CANVAS ───────────────────────────────────────────
    print("\n[2/2] Setting up Canvas...")
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(f"https://{canvas_url}")
    input("    Log into Canvas in the browser, then press Enter here...")
    context.storage_state(path="canvas_session.json")
    print("    Session saved!")

    # Detect courses
    page.goto(f"https://{canvas_url}")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    seen_ids = set()
    canvas_courses = []
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        text = link.get_text(strip=True)
        if "/courses/" in href and "assignments" not in href and "announcements" not in href and "files" not in href:
            parts = href.split("/courses/")
            if len(parts) > 1:
                course_id = parts[1].split("/")[0]
                if course_id not in seen_ids and text and len(text) > 3:
                    seen_ids.add(course_id)
                    canvas_courses.append({"name": text[:60], "id": course_id})

    print("\n    Found these Canvas courses:")
    for i, c in enumerate(canvas_courses):
        print(f"      [{i}] {c['name']}")

    print("\n    Enter the numbers of courses to REMOVE (comma separated),")
    remove_input = input("    or just press Enter to keep all: ").strip()

    if remove_input:
        remove_indices = set(int(x.strip())
                             for x in remove_input.split(",") if x.strip().isdigit())
        canvas_courses = [c for i, c in enumerate(
            canvas_courses) if i not in remove_indices]

    config["canvas_courses"] = canvas_courses
    print(f"\n    Keeping {len(canvas_courses)} Canvas courses.")
    browser.close()

# Save config
with open("config.json", "w") as f:
    json.dump(config, f, indent=2)

print("\n" + "=" * 50)
print("  Setup complete! config.json saved.")
print("  Run scraper.py to fetch your assignments.")
print("=" * 50)
