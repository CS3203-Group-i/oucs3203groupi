import requests
from bs4 import BeautifulSoup
from datetime import datetime

# URL to cs course list
url = "https://ou-public.courseleaf.com/courses/c_s/"

# Get response from url and parse html
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

#This is my edit Test

# Parse to extract list of all courses
courses = []
for block in soup.find_all("p", class_="courseblocktitle"):
    course_name = block.find("strong").get_text(strip=True)
    courses.append(f"{course_name}")

# Getting time of extraction being done
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# Write list of all courses to txt file
with open("backend/data_extraction/data/extracted_classes.txt", "w") as file:
    # Adding extraction time to top of file
    file.write(f"Parsed and extracted at time: {current_time}\n\n") 
    for course in courses:
        file.write(f"{course}\n")

# Print out that the courses have been extracted
print("Courses have been saved to 'extracted_classes.txt'.")
