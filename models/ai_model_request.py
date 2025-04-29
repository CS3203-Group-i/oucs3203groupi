import os
import requests
import re
import json
from collections import defaultdict
import sys

# === UNTOUCHABLE PROMPT: Just here as a reference ===
prompt = """Given the following list of courses with their corresponding sections, times, and days, create an optimal schedule that ensures no time conflicts while taking exactly one section from each course. You can only take one section per course, and the sections must not overlap with each other. Put your final answer within []​. Do not reason step by step.
Courses:
Math 3333:
Section 01: 10-11am T/TR
Section 02: 12-1pm M/W/F
Hist 1234:
Section 01: 10-11am T/TR
Section 02: 2-3pm M/W/F
CS 3203:
Section 01: 10-11am M/W/F
Section 02: 4-5pm M/W/F
ENGR 2002:
Section 01: 3-4pm M/W/F
Section 02: 9-10am T/TR 
"""

# === ACTUAL PROMPT USED ===
base_prompt = """Given the following list of courses with their corresponding sections, times, and days, create an optimal schedule that ensures no time conflicts while taking exactly one section from each course. You must ONLY choose from the sections listed below. Do not invent, add, or infer any additional courses or sections. The sections listed are the ONLY valid options, and you must select one section per course. Please output your final answer in the form of a list of courses and sections, such as [CourseName Section 001 Days MWF Time 10-11:15am, CourseName Section 002 Days TR 6-7pm, ...]. Do not reason step by step, and do not add any extra courses.
Courses:
"""

gemini_api_key = "Not giving this away" 

def generate_with_gemini(prompt):
    if not gemini_api_key:
        raise ValueError("Gemini API key is missing.")
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
    headers = {"Content-Type": "application/json", "x-goog-api-key": gemini_api_key}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))
    return response.json()['candidates'][0]['content']['parts'][0]['text'] if response.status_code == 200 else f"Error {response.status_code}: {response.text}"

def behind_scenes(userInput):
    if userInput == "pdf":
        filename = "backend/ai_filtering/filtered_courses_pdf.txt"
        courses = defaultdict(list)

        with open(filename, "r") as f:
            lines = f.readlines()
            for line in lines:
                match = re.match(r"([A-Z]+\s\d+).*?\| Section: (\d+).*?Meeting days: (\w+).*?Meeting times: ([\d:apm\s\-]+)", line)
                if match:
                    course_code = match.group(1).upper()
                    section = match.group(2).zfill(2)
                    days = match.group(3)
                    if days == "TR":
                        days = "T/TR"
                    time = match.group(4).strip().lower()
                    courses[course_code].append(f"Section {section}: {time} {days}")

        # Combine into full prompt for the model
        course_text = ""
        for course, sections in courses.items():
            course_text += f"{course}:\n"
            for s in sections:
                course_text += f"{s}\n"

        active_prompt = base_prompt + course_text
    elif userInput == "manual":
        filename = "backend/ai_filtering/filtered_courses_manual.txt"
        courses = defaultdict(list)

        with open(filename, "r") as f:
            lines = f.readlines()
            for line in lines:
                match = re.match(r"([A-Z]+\s\d+).*?\| Section: (\d+).*?Meeting days: (\w+).*?Meeting times: ([\d:apm\s\-]+)", line)
                if match:
                    course_code = match.group(1).upper()
                    section = match.group(2).zfill(2)
                    days = match.group(3)
                    if days == "TR":
                        days = "T/TR"
                    time = match.group(4).strip().lower()
                    courses[course_code].append(f"Section {section}: {time} {days}")

        # Combine into full prompt for the model
        course_text = ""
        for course, sections in courses.items():
            course_text += f"{course}:\n"
            for s in sections:
                course_text += f"{s}\n"

        active_prompt = base_prompt + course_text
        #print(active_prompt)

    # === GENERATE OUTPUT ===
    output = generate_with_gemini(active_prompt)
    print("Generated output:\n", output)

    # Save the output into a text file
    output_path = 'models/ai_result.txt'
    with open(output_path, 'w') as file:
        file.write(output)

    print(f"Output saved to {output_path}")

if __name__ == "__main__":
    userInput = sys.argv[2]
    behind_scenes(userInput)

