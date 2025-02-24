import requests
from bs4 import BeautifulSoup

# URL of the course catalog
url = "https://ou-public.courseleaf.com/courses/c_s/"

# Fetch the webpage
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Extract course titles and codes
courses = []
for block in soup.find_all("p", class_="courseblocktitle"):
    course_name = block.find("strong").get_text(strip=True)
    courses.append(f"{course_name}")

# Print results
for course in courses:
    print(course)
