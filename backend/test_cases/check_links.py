import os
import requests
from bs4 import BeautifulSoup

# List of HTML-like files to test
pages = [
    "campus_resources.py",
    "AthleticSchedule.html",
    "HomePage.html",
    "ManualInputPage.html",
    "SubmitFlowchartPage.html"
]

# Suspicious content keywords
suspicious_texts = ["traceback", "error", "debug", "exception", "stack"]

bad_links = []
disclosures = []

print("\n🔍 Starting link and disclosure check...\n")
print("📁 Current working directory:", os.getcwd())

for page in pages:
    path = os.path.join(os.path.dirname(__file__), "../../frontend/pages", page)
    path = os.path.abspath(path)

    print(f"\n🔎 Trying to open: {path}")
    try:
        with open(path, "r") as file:
            print(f"✅ Successfully opened {page}")
            soup = BeautifulSoup(file, "html.parser")

            for a_tag in soup.find_all("a", href=True):
                url = a_tag['href']

                # Skip internal or anchor links
                if url.startswith("#") or url.startswith("/") or url.endswith(".html"):
                    continue

                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code != 200:
                        bad_links.append((url, response.status_code, page))

                    content = response.text.lower()
                    for term in suspicious_texts:
                        if term in content:
                            disclosures.append((url, term, page))
                except Exception as e:
                    bad_links.append((url, str(e), page))

    except FileNotFoundError:
        print(f"❌ File not found: {path}")
    except Exception as e:
        print(f"❌ Error reading {page}: {e}")

# Report results
print("\n🚨 Broken or Problematic External Links:")
if bad_links:
    for url, issue, page in bad_links:
        print(f" - Page: {page} | Link: {url} | Issue: {issue}")
else:
    print("✅ No broken external links found.")

print("\n🚨 Possible Information Disclosures:")
if disclosures:
    for url, keyword, page in disclosures:
        print(f" - Page: {page} | Link: {url} | Keyword found: '{keyword}'")
else:
    print("✅ No info disclosures detected.")

print("\n✅ Test complete.")
