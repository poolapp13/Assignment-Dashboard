from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import json

all_assignments = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(storage_state="session.json")
    page = context.new_page()

    page.goto("https://www.gradescope.com")
    page.wait_for_load_state("networkidle")

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    CURRENT_COURSES = ["26Sp", "26 Spring"]

    course_boxes = soup.find_all("a", class_="courseBox")
    current_courses = []
    for course in course_boxes:
        name = course.find("div", class_="courseBox--name")
        if name:
            course_name = name.get_text(strip=True)
            link = "https://www.gradescope.com" + course.get("href", "")
            if any(keyword in course_name for keyword in CURRENT_COURSES):
                current_courses.append({"name": course_name, "url": link})

    for course in current_courses:
        print(f"Scraping {course['name']}...")
        page.goto(course["url"])
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

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
            if due_date:
                all_assignments.append({
                    "name": name,
                    "course": course["name"],
                    "status": status,
                    "due_date": due_date,
                    "source": "gradescope"
                })

    browser.close()

# Save to JSON
with open("assignments.json", "w") as f:
    json.dump(all_assignments, f, indent=2)

print(f"\nSaved {len(all_assignments)} assignments to assignments.json")
