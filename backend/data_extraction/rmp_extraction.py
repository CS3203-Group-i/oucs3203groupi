import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# --- Step 1: Load and normalize CS professor names from extracted_classnav.txt ---
def extract_unique_names(file_path):
    names = set()
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if "| C S " not in line:
                continue
            match = re.search(r"\|\s*([A-Za-z'\\\-]+,\s+[A-Za-z '\-]+)", line)
            if match:
                last_first = match.group(1).strip()
                if last_first.lower() != "tba":
                    parts = last_first.split(", ")
                    if len(parts) == 2:
                        names.add(f"{parts[1]} {parts[0]}")
    return sorted(names)

# --- Step 2: Setup Selenium ---
options = Options()
# Comment out to run visibly for debugging:
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(), options=options)
wait = WebDriverWait(driver, 5)

# --- Step 3: Search each CS professor and parse results from profile page ---
professors = extract_unique_names("backend/data_extraction/data/extracted_classnav.txt")
with open("rmp_from_classnav.txt", "w", encoding="utf-8") as output:
    for idx, name in enumerate(professors, start=1):
        try:
            print(f"[{idx}/{len(professors)}] Searching: {name}")
            driver.get("https://www.ratemyprofessors.com/search/professors/1596?q=*")

            search_box = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Professor name']")))
            search_box.clear()
            search_box.send_keys(name)
            search_box.send_keys(Keys.RETURN)

            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/professor/') and contains(., 'University of Oklahoma')]")))
            except TimeoutException:
                output.write(f"{name} | Not Found\n")
                print(f"✘ Not found: {name}")
                continue

            links = driver.find_elements(By.XPATH, "//a[contains(@href, '/professor/') and contains(., 'University of Oklahoma')]")
            found = False
            for link in links:
                if name.split()[0].lower() in link.text.lower():
                    link.click()
                    found = True
                    break

            if not found:
                output.write(f"{name} | Not Found\n")
                print(f"✘ Not found: {name}")
                continue

            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)  # Ensure page is fully rendered

            page_text = driver.page_source  # For debug: capture full HTML
            with open(f"debug_page_{idx}.html", "w", encoding="utf-8") as debug_file:
                debug_file.write(page_text)

            try:
                prof_name = driver.find_element(By.TAG_NAME, "h1").text
            except NoSuchElementException:
                prof_name = name
            try:
                rating = driver.find_element(By.XPATH, "//div[contains(@class, 'RatingValue__Numerator') or contains(@class, 'RatingValue__Rating')]").text
            except NoSuchElementException:
                rating = "N/A"
            try:
                would_take_again = driver.find_element(By.XPATH, "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'would take again')]/following-sibling::div").text
            except NoSuchElementException:
                would_take_again = "N/A"
            try:
                difficulty = driver.find_element(By.XPATH, "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'level of difficulty')]/following-sibling::div").text
            except NoSuchElementException:
                difficulty = "N/A"
            try:
                dept = driver.find_element(By.XPATH, "//div[contains(text(),'department at University of Oklahoma')]").text
            except NoSuchElementException:
                dept = "N/A"

            output.write(f"{prof_name} | {dept} | Rating: {rating} | Would take again: {would_take_again} | Difficulty: {difficulty}\n")
            print(f"✔ Found: {name}")

        except Exception as e:
            output.write(f"{name} | Error\n")
            print(f"❗ Error with {name}: {e}")

# --- Clean up ---
driver.quit()
print("✅ Done! Ratings written to rmp_from_classnav.txt")