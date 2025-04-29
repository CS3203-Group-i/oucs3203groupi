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

# Function to read manual from a text file
def read_manual(manual_path):
    manual_courses = set()
    with open(manual_path, "r") as file:
        for line in file:
            line = line.replace('\xa0', ' ')
            #print(line)
            parts = line.strip().split(";")
            if len(parts) >= 3:
                course_title = parts[0].strip()
                course_code = parts[1].strip()
                term = parts[2].strip()
                if "C S" in course_code:
                    course_code = course_code.replace("C S", "CS")
                manual_courses.add(f"{course_code}")
    #print(manual_courses)
    #print(manual_courses)
    return manual_courses
# Function to read RMP data from a text file
def read_rmp_data(rmp_file_path):
    rmp_data = {}
    with open(rmp_file_path, "r") as file:
        for line in file:
            parts = line.strip().split(" | ")
            if len(parts) > 2:
                # Format the professor name as "First Name Last Name"
                name = parts[0].strip()
                score = parts[2].strip()
                # Ensure we have the name in "First Name Last Name" format
                name_parts = name.split()
                if len(name_parts) >= 2:
                    formatted_name = f"{name_parts[0]} {name_parts[1]}"  # "First Name Last Name"
                    rmp_data[formatted_name] = score
    return rmp_data

# Modified filter_courses function to include RMP data
def filter_courses(cs_file_path, manual_path, pdf_path, rmp_file_path):

    # Initialize the filtered courses lists for PDF and manual
    filtered_courses_pdf = []
    filtered_courses_manual = []

    # Load RMP data
    rmp_data = read_rmp_data(rmp_file_path)

    # Check if the PDF file exists and process the PDF data
    if os.path.exists(pdf_path):
        courses = read_courses(cs_file_path)
        green_courses = extract_text_from_pdf_green_boxes_image_analysis(pdf_path)

        # Process the green courses from the PDF and extract the course IDs
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

        # Find the intersection of course IDs from PDF and CS file
        for course_info in courses:
            parts = course_info.split()
            course_id_file = f"{parts[0]} {parts[1]}" if len(parts) >= 2 else parts[0]
            if course_id_file in extracted_texts_id_only:

                # Get the professor's name from the full course info and format it
                #print(course_info)
                tmp_prof_finder = course_info.split("|")
                prof = tmp_prof_finder[2].replace("Teacher: ", "").replace(",","")
                prof_swapped = " ".join(prof.split()[::-1])
                #print(prof_swapped)
                professor_name = prof_swapped 
                #professor_name = parts[1].strip()  # Assuming the professor's name is in the 6th column

                rmp_score = rmp_data.get(professor_name, "N/A")
                #print(rmp_score)
                # Add RMP score to the course information
                full_course_info_with_rmp = f"{course_info} | Rate My Professor: {rmp_score}"
                filtered_courses_pdf.append(full_course_info_with_rmp)  # Add the full course info with RMP score

    # Save filtered PDF courses to a separate file
    if filtered_courses_pdf:
        with open("backend/ai_filtering/filtered_courses_pdf.txt", "w") as f_pdf:
            for course in filtered_courses_pdf:
                f_pdf.write(course + "\n")

    # Check if the manual file exists and process the manual data
    if os.path.exists(manual_path):
        manual_courses = read_manual(manual_path)

        # Iterate through manual_courses to match course IDs
        for course_info in manual_courses:
            # Extract the course ID from manual_courses (it should be in the format: "CS 1213 Programming for Non-Majors with Python | Term: Fall 2025")
            parts = course_info.split()
            course_id = f"{parts[0]} {parts[1]}"  # This gives the course code in the format "CS 1213"

            # If the course ID exists in courses_id_only and is not already in filtered_courses_manual
            course_id = course_id.replace("G", "")

            if course_id in courses_id_only and course_info not in filtered_courses_manual:
                # Iterate through the 'courses' to get the full set of information for the matching course
                for full_course_info in courses:
                    full_parts = full_course_info.split()
                    full_course_id = f"{full_parts[0]} {full_parts[1]}"  # Extract the course ID from the full course info

                    if course_id == full_course_id:
                        # Get the professor's name from the full course info and format it
                        tmp_prof_finder = full_course_info.split("|")
                        prof = tmp_prof_finder[2].replace("Teacher: ", "").replace(",","")
                        prof_swapped = " ".join(prof.split()[::-1])
                        #print(prof_swapped)
                        professor_name = prof_swapped 
                        #professor_name = parts[1].strip()  # Assuming the professor's name is in the 6th column
  
                        rmp_score = rmp_data.get(professor_name, "N/A")
                        #print(rmp_score)
                        # Add RMP score to the course information
                        full_course_info_with_rmp = f"{full_course_info} | Rate My Professor: {rmp_score}"
                        filtered_courses_manual.append(full_course_info_with_rmp)  # Add the full course info with RMP score

    # Save filtered manual courses to a separate file
    if filtered_courses_manual:
        with open("backend/ai_filtering/filtered_courses_manual.txt", "w") as f_manual:
            for course in filtered_courses_manual:
                f_manual.write(course + "\n")

# Example usage
cs_file_path = 'backend/data_extraction/data/extracted_classnav.txt'  # Path to your CS courses text file
manual_path = 'backend/data_extraction/user_data/courseData.txt'  # Path to your manual text file
pdf_path = 'backend/data_extraction/user_data/flowchart.pdf'  # Path to your PDF file
rmp_file_path = 'backend/data_extraction/data/extracted_rmp.txt'  # Path to your RMP data file

# Collect the filtered course details and save them to separate files
filter_courses(cs_file_path, manual_path, pdf_path, rmp_file_path)
