from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import time
from selenium.webdriver.chrome.options import Options

# Set Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run without GUI
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Load the Fall 2025 semester directly
driver.get("https://classnav.ou.edu/#semester/202510")

# Wait until the table loads
wait = WebDriverWait(driver, 20)
wait.until(EC.presence_of_element_located((By.ID, "clist")))

# Set table to show 100 entries per page
Select(wait.until(EC.presence_of_element_located((By.NAME, "clist_length")))).select_by_value("100")
time.sleep(3)  # Allow table to populate

# Storage for all course rows
all_data = []
page_num = 1

while True:
    print(f"Scraping page {page_num}")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find("table", id="clist")
    rows = table.find("tbody").find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 8:
            crn = cols[1].text.strip()
            subject = cols[2].text.strip()
            course = cols[3].text.strip()
            section = cols[4].text.strip()
            title = cols[5].text.strip()
            print(title)
            instructor = cols[6].text.strip()
            dates = cols[7].text.strip()
            all_data.append([crn, subject, course, section, title, instructor, dates])

    # Try to go to the next page
    try:
        next_btn = driver.find_element(By.ID, "clist_next")
        if "disabled" in next_btn.get_attribute("class"):
            print("Reached last page.")
            break
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(2)
        page_num += 1
    except Exception as e:
        print("Error during pagination:", e)
        break

# Get timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Set output path
output_path = Path("data/extracted_classnav.txt")
output_path.parent.mkdir(parents=True, exist_ok=True)

# Write results to file
with open(output_path, "w") as f:
    f.write(f"ClassNav course extraction\nTimestamp: {timestamp}\n")
    f.write("=" * 100 + "\n")
    f.write("CRN | Subject | Course | Section | Title | Instructor | Dates\n")
    f.write("=" * 100 + "\n")
    for row in all_data:
        f.write(" | ".join(row) + "\n")

print(f"\nFinished scraping {len(all_data)} classes.")
print(f"Data saved to: {output_path}")

# Close browser
driver.quit()
