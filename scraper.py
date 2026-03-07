from dateutil import parser as dateparser
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

base_url = f"https://{config['canvas_url']}"
# Create sessions if they don't exist
if not os.path.exists("session.json") or not os.path.exists("canvas_session.json"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        if not os.path.exists("session.json"):
            context = browser.new_context()
            page = context.new_page()
            page.goto("https://www.gradescope.com")
            input("Log into Gradescope, then press Enter...")
            context.storage_state(path="session.json")
            print("Gradescope session saved!")
            browser.close()

        if not os.path.exists("canvas_session.json"):
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(f"https://{config['canvas_url']}")
            input("Log into Canvas, then press Enter...")
            context.storage_state(path="canvas_session.json")
            print("Canvas session saved!")
            browser.close()


def normalize_date(date_str):
    # If it's already a full datetime string, return as is
    if "-" in date_str and ":" in date_str and len(date_str) > 15:
        return date_str
    # Otherwise parse and convert Canvas format like "Mar 8 at 11:59pm"
    cleaned = date_str.replace(" at ", " ")
    dt = dateparser.parse(cleaned, default=datetime(2026, 1, 1))
    return dt.strftime("%Y-%m-%d %H:%M:%S -0500")


all_assignments = []

# Gradescope scraper
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(storage_state="session.json")
    page = context.new_page()

    page.goto("https://www.gradescope.com")
    page.wait_for_load_state("networkidle")

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    current_courses = config["gradescope_courses"]

    for course in current_courses:
        print(f"Scraping {course['name']}...")
        page.goto(course["url"])
        page.wait_for_load_state("networkidle")

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        rows = soup.find_all("tr", class_=["odd", "even"])
        for row in rows:
            name_cell = row.find(["td", "th"], class_="table--primaryLink")
            if not name_cell:
                continue

            name = name_cell.get_text(strip=True)

            status_cell = row.find("td", class_="submissionStatus")
            status = status_cell.get_text(strip=True) if status_cell else ""

            due_times = row.find_all(
                "time", class_="submissionTimeChart--dueDate")
            due_date = None
            for t in due_times:
                if "Late Due Date" not in t.get_text():
                    due_date = t.get("datetime")
                    break

            # Only include assignments with a due date
            if due_date and "Submitted" not in status and "/" not in status:
                all_assignments.append({
                    "name": name,
                    "course": course["name"],
                    "status": status,
                    "due_date": normalize_date(due_date),
                    "source": "gradescope"
                })

    browser.close()

# Canvas scraper
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(storage_state="canvas_session.json")
    page = context.new_page()

    base_url = f"https://{config['canvas_url']}"

    canvas_courses = config["canvas_courses"]

    for course in canvas_courses:
        print(f"\nScraping {course['name']}...")

        # Scrape assignments and quizzes
        for section in ["assignments", "quizzes"]:
            page.goto(f"{base_url}/courses/{course['id']}/{section}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            rows = soup.find_all("div", class_="ig-row")
            for row in rows:
                name = row.find(["div", "a"], class_="ig-title")
                due = row.find("div", class_="assignment-date-due")
                score = row.find("div", class_="js-score")

                name_text = name.get_text(strip=True) if name else ""
                due_text = due.find(
                    "span", class_="screenreader-only").get_text(strip=True) if due else ""
                score_text = score.find("span", class_="non-screenreader").get_text(
                    strip=True) if score and score.find("span", class_="non-screenreader") else ""

                if not name_text or not due_text or "-/" not in score_text:
                    continue

                # Click into assignment to check submission status
                link = row.find("a", class_="ig-title")
                if link:
                    href = link.get("href", "")
                    full_url = base_url + \
                        href if href.startswith("/") else href
                    page.goto(full_url)
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(500)

                    detail_html = page.content()
                    detail_soup = BeautifulSoup(detail_html, "html.parser")
                    tracker = detail_soup.find(
                        class_="assignment-student-submission-tracker")

                    if tracker and "Submitted" in tracker.get_text():
                        print(f"  Skipping {name_text} - already submitted")
                        # Go back to assignments page
                        page.goto(
                            f"{base_url}/courses/{course['id']}/{section}")
                        page.wait_for_load_state("networkidle")
                        page.wait_for_timeout(500)
                        continue

                all_assignments.append({

                    "name": name_text,
                    "course": course["name"],
                    "status": score_text,
                    "due_date": normalize_date(due_text),
                    "source": "canvas"
                })
                print(f"  {name_text} | {due_text} | {score_text}")

                # Go back
                page.goto(f"{base_url}/courses/{course['id']}/{section}")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(100)

    browser.close()


# Get all gradescope assignment names (lowercase for comparison)
gradescope_names = set(a["name"].lower()
                       for a in all_assignments if a["source"] == "gradescope")

# Filter out canvas assignments that already exist in gradescope
filtered_assignments = []
for a in all_assignments:
    if a["source"] == "canvas":
        if a["name"].lower() not in gradescope_names:
            filtered_assignments.append(a)
    else:
        filtered_assignments.append(a)

all_assignments = filtered_assignments


# Save everything to JSON
with open("assignments.json", "w") as f:
    json.dump(all_assignments, f, indent=2)

print(
    f"\nTotal: {len(all_assignments)} unsubmitted assignments saved to assignments.json")
