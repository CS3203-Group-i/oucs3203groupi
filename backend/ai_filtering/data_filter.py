import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import cv2
import numpy as np
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox
import re

def extract_text_from_pdf_green_boxes_image_analysis(pdf_path):
    extracted_data = []
    try:
        # Convert the first page of the PDF to a list of PIL Images
        images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=1)
        if not images:
            return "Error: Could not convert PDF to image."
        img_pil = images[0]
        img_cv = np.array(img_pil)
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR) # Convert to BGR for OpenCV

        # --- Identify Green Regions using OpenCV ---
        lower_green = np.array([0, 100, 0])   # Adjust these values based on your green color
        upper_green = np.array([100, 255, 100])
        mask = cv2.inRange(img_cv, lower_green, upper_green)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        green_box_regions_pixels = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            green_box_regions_pixels.append((x, y, x + w, y + h))

        # --- Extract Text Elements using pdfminer.six and Associate ---
        for page_layout in extract_pages(pdf_path):
            for i, (gx0, gy0, gx1, gy1) in enumerate(green_box_regions_pixels):
                region_name = f"green_box_{i+1}"
                text_in_region = []
                for element in page_layout:
                    if isinstance(element, LTTextBox):
                        # Convert PDF coordinates to pixel coordinates (approximation)
                        pdf_width = page_layout.width
                        pdf_height = page_layout.height
                        image_width = img_pil.width
                        image_height = img_pil.height

                        tx0, ty0, tx1, ty1 = element.bbox
                        px0 = int(tx0 / pdf_width * image_width)
                        py0 = int((pdf_height - ty1) / pdf_height * image_height) # Invert Y
                        px1 = int(tx1 / pdf_width * image_width)
                        py1 = int((pdf_height - ty0) / pdf_height * image_height)

                        # Check if the entire text box is within the green region
                        if (gx0 <= px0 and px1 <= gx1 and gy0 <= py0 and py1 <= gy1):
                            text_in_region.append(element.get_text().strip())

                if text_in_region:
                    extracted_data.append({"region": region_name, "text": " ".join(text_in_region)})

    except FileNotFoundError:
        return f"Error: PDF file not found at {pdf_path}"
    except Exception as e:
        return f"Error during processing: {e}"
    #print(extracted_data)
    return extracted_data

# Function to read courses from a text file and filter for CS courses
# Function to read courses from a text file and filter for CS courses
def read_courses(cs_file_path):
    courses = set()
    with open(cs_file_path, "r") as file:
        for line in file:
            if " C S " in line or " MATH " in line:
                parts = line.split('|')
                if len(parts) >= 6:  # Ensure we have enough parts
                    subject = parts[1].strip().replace(" ", "")
                    course_code = parts[2].strip()
                    course_title = parts[4].strip()
                    section = parts[3].strip()  # Assuming teacher is here
                    teacher = parts[5].strip() # Assuming date/time is here
                    date = parts[6].strip()
                    # Remove 'G' from the course code if it starts with 'G'
                    if course_code.startswith('G'):
                        course_code = course_code[1:]
                    courses.add(f"{subject} {course_code} {course_title} | Section: {section} | Teacher: {teacher} | Dates: {date}")

    return courses

# Function to read preferences from a text file
def read_preferences(preferences_file_path):
    preferences = set()
    with open(preferences_file_path, "r") as file:
        for line in file:
            preferences.add(line.strip())
    return preferences

# Main function to process all files and filter the courses
def filter_courses(cs_file_path, preferences_file_path, pdf_path):
    courses = read_courses(cs_file_path)
    preferences = read_preferences(preferences_file_path)
    green_courses = extract_text_from_pdf_green_boxes_image_analysis(pdf_path)
    print(courses)

    #print()
    # Find intersection of all three sets
    
    extracted_texts = []
    extracted_texts_id_only = []
    for item in green_courses:
        text = item['text']
        parts = text.split()
        combined_text_parts = []
        include_rest = True
        for part in parts:
            if "Prereq" in part:
                include_rest = False
            if include_rest:
                combined_text_parts.append(part)

        if combined_text_parts:
            extracted_texts.append(" ".join(combined_text_parts))
            extracted_texts_id_only.append(f"{combined_text_parts[0]} {combined_text_parts[1]}")

    courses_id_only = set()
    course_map = {}
    for course_info in courses:
        parts = course_info.split()
        courses_id_only.add(f"{parts[0]} {parts[1]}")


    #print(courses_id_only)


    #print(extracted_texts)
    #print(courses)
    #print(courses)
    filtered_courses = courses_id_only.intersection(set(extracted_texts_id_only))
    print(filtered_courses)

    print("\nFull Information of Intersected Courses:")
    for course_info in courses:
        parts = course_info.split()
        course_id_file = f"{parts[0]} {parts[1]}" if len(parts) >= 2 else parts[0]
        if course_id_file in filtered_courses:
            print(course_info)
    # Print the extracted texts
    #for text in extracted_texts:
        #print(text)

    # right here, I want you to make something that will just the course code / subject from courses

    filtered_courses = courses.intersection(set(extracted_texts))
    #print("\nIntersection of CS Courses and Extracted Texts:")
    #print(filtered_courses)

    # Create a set of course IDs from the 'courses' read from the file
    course_ids_from_file = set()
    for course_info in courses:
        parts = course_info.split(" ", 2) # Split into Subject Code and the rest
        if len(parts) >= 2:
            course_ids_from_file.add(f"{parts[0]} {parts[1]}")

    filtered_courses_ids = course_ids_from_file.intersection(extracted_texts)
    #print(filtered_courses_ids)
    #print(extracted_texts)
    #print(courses)
    #print("\nIntersection of Course IDs:")
    #print(filtered_courses_ids)

    # Print the filtered courses
    #if filtered_courses:
    #    print("Filtered Courses (CS, Preferences, and Green-highlighted):")
     #   for course in filtered_courses:
       #     print(course)
   # else:
      #  print("No matching courses found.")
                                           
# Example usage
cs_file_path = 'backend/data_extraction/data/extracted_classnav.txt'  # Path to your CS courses text file
preferences_file_path = 'backend/data_extraction/user_data/courseData.txt'  # Path to your preferences text file
pdf_path = 'tmp.pdf'  # Path to your PDF file

filter_courses(cs_file_path, preferences_file_path, pdf_path)
