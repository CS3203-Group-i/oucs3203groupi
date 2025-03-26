import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import cv2
import numpy as np
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox

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

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
    except FileNotFoundError:
        return f"Error: File not found at {pdf_path}"
    except Exception as e:
        return f"Error reading PDF: {e}"
    return text

# Function to read courses from a text file and filter for CS courses
def read_cs_courses(cs_file_path):
    cs_courses = set()
    with open(cs_file_path, "r") as file:
        for line in file:
            if "CS" in line:  # Filter for CS courses
                cs_courses.add(line.strip())
    return cs_courses

# Function to read preferences from a text file
def read_preferences(preferences_file_path):
    preferences = set()
    with open(preferences_file_path, "r") as file:
        for line in file:
            preferences.add(line.strip())
    return preferences

# Main function to process all files and filter the courses
def filter_courses(cs_file_path, preferences_file_path, pdf_path):
    cs_courses = read_cs_courses(cs_file_path)
    preferences = read_preferences(preferences_file_path)
    green_courses = extract_text_from_pdf_green_boxes_image_analysis(pdf_path)

    #print()
    # Find intersection of all three sets
    #filtered_courses = cs_courses.intersection(preferences, green_courses)
    
    extracted_texts = []
    for item in green_courses:
        text = item['text']
        # Split the text into parts based on spaces
        parts = text.split()
        if len(parts) > 1:
            # Combine the first two parts (e.g., "CS 4173" and "Computer Security")
            combined_text = " ".join(parts[:2])
            extracted_texts.append(combined_text)
        else:
            # If there's only one part, append it as is
            extracted_texts.append(text)

    # Print the extracted texts
    for text in extracted_texts:
        print(text)

    # Print the filtered courses
    #if filtered_courses:
    #    print("Filtered Courses (CS, Preferences, and Green-highlighted):")
     #   for course in filtered_courses:
       #     print(course)
   # else:
      #  print("No matching courses found.")

# Example usage
cs_file_path = '../data_extraction/data/extracted_classnav.txt'  # Path to your CS courses text file
preferences_file_path = '../test_cases/fake_input.txt'  # Path to your preferences text file
pdf_path = 'tmp.pdf'  # Path to your PDF file

filter_courses(cs_file_path, preferences_file_path, pdf_path)
