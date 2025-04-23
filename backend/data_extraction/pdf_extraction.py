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