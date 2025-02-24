import requests
from bs4 import BeautifulSoup

# URL to cs course list
url = "https://ou-public.courseleaf.com/courses/c_s/"

# Get response from url and parse html
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Parse to extract list of all courses
courses = []
for block in soup.find_all("p", class_="courseblocktitle"):
    course_name = block.find("strong").get_text(strip=True)
    courses.append(f"{course_name}")

# Write list of all courses to txt file
with open("backend/data_extraction/data/extracted_classes.txt", "w") as file:
    for course in courses:
        file.write(f"{course}\n")

# Print out that the courses have been extracted
print("Courses have been saved to 'extracted_classes.txt'.")
