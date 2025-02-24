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

# Write results to a text file
with open("backend/data_extraction/data/extracted_classes.txt", "w") as file:
    for course in courses:
        file.write(f"{course}\n")

print("Courses have been saved to 'extracted_classes.txt'.")
