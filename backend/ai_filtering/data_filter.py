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

# importing pdf extraction
from data_extraction.pdf_extraction import extract_text_from_pdf_green_boxes_image_analysis

# Reading in classnav data
def read_courses(cs_file_path):
    courses = set()
    with open(cs_file_path, "r") as file:
        for line in file:
            # Conditional for only C S or MATH courses
            if " C S " in line or " MATH " in line:
                parts = line.split('|')
                if len(parts) >= 6:  
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
                    # Graduate level classes not supported yet
                    if course_code.startswith('G'):
                        course_code = course_code[1:]
                    courses.add(f"{subject} {course_code} {course_title} | Section: {section} | Teacher: {teacher} | Dates: {date} | Meeting days: {meeting_days} | Meeting times: {meeting_times} | Location: {location}")

    # Return all cs and math courses
    return courses

# Function to read manual input from a text file
def read_manual(manual_path):

    # Makes a set of the manual courses to be filled up
    manual_courses = set()

    # Opens up manual  file
    with open(manual_path, "r") as file:

        # Goes through each line, splits and reformats it
        for line in file:
            line = line.replace('\xa0', ' ')
            #print(line)
            parts = line.strip().split(";")
            if len(parts) >= 3:
                course_title = parts[0].strip()
                course_code = parts[1].strip()
                term = parts[2].strip()

                # Conditional for further consistency in formatting
                if "C S" in course_code:
                    course_code = course_code.replace("C S", "CS")
                manual_courses.add(f"{course_code}")

    return manual_courses

# Function to read RMP data from a text file
def read_rmp_data(rmp_file_path):

    # Goes through rmp file and stores data

    # Need to reformat everything since other extraction goes First Name Last Name
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
                    formatted_name = f"{name_parts[0]} {name_parts[1]}"  # First Name Last Name
                    rmp_data[formatted_name] = score

    return rmp_data

# Filters through all courses to find intersecting ones based on actual courses and manual/pdf input
def filter_courses(cs_file_path, manual_path, pdf_path, rmp_file_path):

    # Initialize the filtered courses lists for PDF and manual
    filtered_courses_pdf = []
    filtered_courses_manual = []

    # Get RMP data
    rmp_data = read_rmp_data(rmp_file_path)

    # Create a set of course IDs only from the 'courses' read from the file for intersection
    courses = read_courses(cs_file_path)
    courses_id_only = set()
    for course_info in courses:
        parts = course_info.split()
        courses_id_only.add(f"{parts[0]} {parts[1]}")

    # Check if the PDF file exists and process the PDF data if it does
    if os.path.exists(pdf_path):

        # Green text boxes are the ones used by advisors
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

                # Prereqs not supported yet
                if "Prereq" in part:
                    include_rest = False
                if include_rest:
                    combined_text_parts.append(part)

            if combined_text_parts:
                extracted_texts.append(" ".join(combined_text_parts))
                extracted_texts_id_only.append(f"{combined_text_parts[0]} {combined_text_parts[1]}")

        

        # Find the intersection of course IDs from PDF and ClassNav file
        for course_info in courses:
            parts = course_info.split()
            course_id_file = f"{parts[0]} {parts[1]}" if len(parts) >= 2 else parts[0]
            if course_id_file in extracted_texts_id_only:

                # Get the professor's name from the full course info and format it
                tmp_prof_finder = course_info.split("|")
                prof = tmp_prof_finder[2].replace("Teacher: ", "").replace(",","")
                prof_swapped = " ".join(prof.split()[::-1])
                professor_name = prof_swapped 

                # Tag on rmp score, N/A if not extracted or available
                rmp_score = rmp_data.get(professor_name, "N/A")
                
                # Add RMP score to the full course information
                full_course_info_with_rmp = f"{course_info} | Rate My Professor: {rmp_score}"
                filtered_courses_pdf.append(full_course_info_with_rmp)  # Add the full course info with RMP score

    # Save filtered PDF courses to a separate file
    if filtered_courses_pdf:
        with open("backend/ai_filtering/filtered_courses_pdf.txt", "w") as f_pdf:
            for course in filtered_courses_pdf:
                f_pdf.write(course + "\n")

    # Check if the manual input file exists and process the manual input data ifso
    if os.path.exists(manual_path):

        # Get all the manually inputted courses
        manual_courses = read_manual(manual_path)

        # Iterate through manual_courses to match course IDs (intersecting)
        for course_info in manual_courses: 

            # Extract the course ID from manual_courses
            # OG format was "CS 1213 Programming for Non-Majors with Python | Term: Fall 2025")
            parts = course_info.split()

            # Getting only course id aka CS 1213
            course_id = f"{parts[0]} {parts[1]}"  

            # Removes G if present such as CS G4513, graduate level classes not supported yet
            course_id = course_id.replace("G", "")

            # Conditional that checks if course id in manual input matches course id in ClassNav
            if course_id in courses_id_only:
                
                # Iterate through the 'courses' to get the full set of information for the matching course
                for full_course_info in courses:
                    full_parts = full_course_info.split()
                    full_course_id = f"{full_parts[0]} {full_parts[1]}"  # Extract the course ID from the full course info

                    # Extra conditional to check if course id in manual input matches course id in ClassNav 
                    # Edge case, previous conditonal should have caught this but ocassionally doesn't due to formatting
                    if course_id == full_course_id:
                        
                        # Conditional that checks for labs and disc
                        if 'Lab-' in full_course_info or 'Disc-' in full_course_info:

                        # Replace last digit of the second part with '0'
                        # Helps AI still designate the course in the final result
                            prefix = full_parts[1][:-1]
                            full_parts[1] = prefix + '0'
                            full_course_id = f"{full_parts[0]} {full_parts[1]}"

                            # Recombine into full_course_info with course ID updated for lab/disc
                            full_course_info = ' '.join(full_parts) + ' ' + ' '.join(full_parts[2:])  # append the rest back
                            #print(full_course_info)
                            
                        # Get the professor's name from the full course info and format it
                        tmp_prof_finder = full_course_info.split("|")
                        prof = tmp_prof_finder[2].replace("Teacher: ", "").replace(",","")
                        prof_swapped = " ".join(prof.split()[::-1])
                        professor_name = prof_swapped 
    
                        # Get rmp if applicable
                        rmp_score = rmp_data.get(professor_name, "N/A")

                        # Combines full course info with rmp
                        full_course_info_with_rmp = f"{full_course_info} | Rate My Professor: {rmp_score}"
                        filtered_courses_manual.append(full_course_info_with_rmp)  

    # Save filtered manually inputted courses to a separate file
    if filtered_courses_manual:
        with open("backend/ai_filtering/filtered_courses_manual.txt", "w") as f_manual:
            for course in filtered_courses_manual:
                f_manual.write(course + "\n")

# Paths
cs_file_path = 'backend/data_extraction/data/extracted_classnav.txt'  # Path to your CS courses ClassNav
manual_path = 'backend/data_extraction/user_data/courseData.txt'  # Path to your manually inputted text file
pdf_path = 'backend/data_extraction/user_data/flowchart.pdf'  # Path to your PDF inputted file
rmp_file_path = 'backend/data_extraction/data/extracted_rmp.txt'  # Path to your RMP extracted data

# Collect the filtered course details and save them to separate files based on paths
filter_courses(cs_file_path, manual_path, pdf_path, rmp_file_path)
