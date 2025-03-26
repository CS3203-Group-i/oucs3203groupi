import sys
import re
from pathlib import Path

def normalize(text):
    # Replace non-breaking spaces with normal spaces and collapse multiple spaces
    return re.sub(r"\s+", " ", text.replace("\u00A0", " ")).strip()

# Load full course rows from file and normalize each line
def load_courses_from_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return {
            normalize(line)
            for line in file
            if line.strip() and "|" in line and not line.startswith("CRN")
        }

# Normalize input and check for existence
def is_class(full_row, course_set):
    return normalize(full_row) in course_set

# Load dataset
classnav_courses = load_courses_from_file("backend/data_extraction/data/extracted_classnav.txt")

# Run tests
if __name__ == "__main__":
    # Edge case
    empty_courses = set()
    assert is_class("33487 | A HI | 3303 | 025 | Renaissance Art in Italy | Duclaux, Kirk | Aug 25 – Dec 19", empty_courses) == False

    test_cases = [
        ("", False),
        ("33487 | A HI | 3303 | 025 | Renaissance Art in Italy | Duclaux, Kirk | Aug 25 - Dec 19", True),
        ("33487 | A HI | 3303 | 025 | Renaissance Art in Germany | Duclaux, Kirk | Aug 25 – Dec 19", False),
        ("99999 | A HI | 3303 | 025 | Renaissance Art in Italy | Duclaux, Kirk | Aug 25 – Dec 19", False),
        ("33487 | A HI | 3303 | 025 | Renaissance Art in Italy | TBA | Aug 25 – Dec 19", False),
    ]

    all_passed = True

    for course_line, expected in test_cases:
        result = is_class(course_line, classnav_courses)
        if result == expected:
            print(f"Passed: {course_line}")
        else:
            print(f"Failed: {course_line} | Expected {expected}, got {result}")
            all_passed = False

    if all_passed:
        print("\nAll tests passed.")
    else:
        print("\nSome tests failed.")
        sys.exit(1)
