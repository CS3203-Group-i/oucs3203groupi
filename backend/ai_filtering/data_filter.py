import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import cv2
import numpy as np
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox

import sys
import os

# Add the parent directory of 'backend' to sys.path (the root of the project)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))

# Now, you can import using the absolute import path
from data_extraction.pdf_extraction import extract_text_from_pdf_green_boxes_image_analysis

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
                    section = parts[3].strip()  
                    teacher = parts[5].strip()           
                    date = parts[6].strip()
                    meeting_days = parts[7].strip()
                    meeting_times = parts[8].strip()
                    location = parts[9].strip()
                    # Remove 'G' from the course code if it starts with 'G'
                    if course_code.startswith('G'):
                        course_code = course_code[1:]
                    courses.add(f"{subject} {course_code} {course_title} | Section: {section} | Teacher: {teacher} | Dates: {date} | Meeting days: {meeting_days} | Meeting times: {meeting_times} | Location: {location}")

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

    # Process green courses and extract text
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

    # Create a set of course IDs from the 'courses' read from the file
    courses_id_only = set()
    for course_info in courses:
        parts = course_info.split()
        courses_id_only.add(f"{parts[0]} {parts[1]}")

    filtered_courses = courses_id_only.intersection(set(extracted_texts_id_only))

    # Now, we want to save all the final information (instead of printing it)
    filtered_course_details = []  # List to hold all the final filtered course details
    for course_info in courses:
        parts = course_info.split()
        course_id_file = f"{parts[0]} {parts[1]}" if len(parts) >= 2 else parts[0]
        if course_id_file in filtered_courses:
            filtered_course_details.append(course_info)

    # You can either return this list or save it to a file
    return filtered_course_details  # Or save it to a file as needed

# Example usage
cs_file_path = 'backend/data_extraction/data/extracted_classnav.txt'  # Path to your CS courses text file
preferences_file_path = 'backend/data_extraction/user_data/courseData.txt'  # Path to your preferences text file
pdf_path = 'backend/data_extraction/user_data/flowchart.pdf'  # Path to your PDF file

# Collect the filtered course details
filtered_courses = filter_courses(cs_file_path, preferences_file_path, pdf_path)

# For example, to save the filtered courses to a text file
with open("backend/ai_filtering/filtered_courses.txt", "w") as f:
    for course in filtered_courses:
        f.write(course + "\n")
