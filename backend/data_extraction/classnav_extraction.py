from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import time

# === Chrome setup ====
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# === Load Fall 2025 directly
driver.get("https://classnav.ou.edu/#semester/202510")
wait = WebDriverWait(driver, 15)

# === Wait for class table, set to 100 entries per page
wait.until(EC.presence_of_element_located((By.ID, "clist")))
Select(wait.until(EC.presence_of_element_located((By.NAME, "clist_length")))).select_by_value("100")
time.sleep(3)

# === File output setup ===
output_path = Path("backend/data_extraction/data/extracted_classnav.txt")
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w", encoding="utf-8") as output_file:
    output_file.write(f"ClassNav course extraction (Clean Table Format)\nTimestamp: {datetime.now()}\n")
    output_file.write("-" * 140 + "\n")
    output_file.write(
        "CRN   | Subject | Course | Section | Title                     | Instructor        | Dates            | "
        "Meeting Days | Meeting Times     | Location                     | Seats Remaining\n"
    )
    output_file.write("-" * 140 + "\n")

    page_num = 1
    while True:
        print(f"\n📄 Scraping page {page_num}...")

        # Expand all rows at once
        driver.execute_script("""
            document.querySelectorAll('#clist tbody .odd td:first-child span.ui-icon, #clist tbody .even td:first-child span.ui-icon')
                .forEach(e => e.click());
        """)
        time.sleep(2.5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table", id="clist")
        all_rows = table.find("tbody").find_all("tr")

        i = 0
        while i < len(all_rows):
            main = all_rows[i]

            # Skip summary rows like Quick Facts
            if "Quick Facts" in main.get_text():
                i += 1
                continue

            cols = main.find_all("td")
            if len(cols) < 9:
                i += 1
                continue

            crn = cols[1].get_text(strip=True)
            subject = cols[2].get_text(strip=True)
            course = cols[3].get_text(strip=True)
            section = cols[4].get_text(strip=True)
            title = cols[5].get_text(strip=True)
            instructor = cols[6].get_text(strip=True)
            dates = cols[7].get_text(strip=True)
            seats = cols[8].get_text(strip=True)

            # default meeting data
            date_range = meeting_times = meeting_days = meeting_location = "N/A"

            if i + 1 < len(all_rows):
                expanded = all_rows[i + 1]
                table = expanded.select_one("table.MeetingDetails")

                if table:
                    date_ranges_list = []
                    meeting_times_list = []
                    meeting_days_list = []
                    meeting_locations_list = []

                    for r in table.select("tbody tr"):
                        cells = r.find_all("td")
                        if (
                            len(cells) >= 4 and
                            "Final Exam" not in cells[0].text and
                            "Quick Facts" not in cells[0].text and
                            "Schedule:" not in cells[0].text
                        ):
                            date_ranges_list.append(cells[0].get_text(strip=True))
                            meeting_times_list.append(cells[1].get_text(strip=True))
                            meeting_locations_list.append(cells[2].get_text(strip=True))
                            meeting_days_list.append(cells[3].get_text(strip=True))

                    date_range = " | ".join(date_ranges_list) or "N/A"
                    meeting_times = " | ".join(meeting_times_list) or "N/A"
                    meeting_location = " | ".join(meeting_locations_list) or "N/A"
                    meeting_days = " | ".join(meeting_days_list) or "N/A"

            # write clean formatted row
            output_file.write(
                f"{crn.ljust(6)}| {subject.ljust(7)}| {course.ljust(6)}| {section.ljust(8)}| {title.ljust(27)}| "
                f"{instructor.ljust(18)}| {dates.ljust(18)}| {meeting_days.ljust(12)}| {meeting_times.ljust(20)}| "
                f"{meeting_location.ljust(30)}| {seats.ljust(15)}\n"
            )

            i += 2  # skip expanded row

        # Next page
        try:
            next_btn = driver.find_element(By.ID, "clist_next")
            if "disabled" in next_btn.get_attribute("class"):
                print("✅ Reached last page.")
                break
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(3)
            page_num += 1
        except Exception as e:
            print("⚠️ Pagination error:", e)
            break

driver.quit()
print(f"\n✅ Done! Data saved to: {output_path}")
