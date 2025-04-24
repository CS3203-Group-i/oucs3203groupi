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
    all_passed = True

    # Edge case: empty course set should return False
    if not is_class("33487 | A HI | 3303 | 025 | Renaissance Art in Italy | Duclaux, Kirk | Aug 25 - Dec 19", set()):
        print("Passed edge case: empty course set")
    else:
        print("Failed edge case: empty course set")
        all_passed = False

    # Valid course test: should return True
    test_true = "33487 | A HI | 3303 | 025 | Renaissance Art in Italy | Duclaux, Kirk | Aug 25 - Dec 19"
    if is_class(test_true, classnav_courses):
        print("Passed: known existing course")
    else:
        print("Failed: known existing course - Expected True, got False")
        all_passed = False

    # Invalid course test: should return False
    test_false = "33487 | A HI | 3303 | 025 | Renaissance Art in Germany | Duclaux, Kirk | Aug 25 - Dec 19"
    if not is_class(test_false, classnav_courses):
        print("Passed: known non-existing course")
    else:
        print("Failed: non-existing course - Expected False, got True")
        all_passed = False

    # Boundary test: large input
    boundary_test = "Aaaabasdbkasjdblkajsdblkasjdlbkjasdlkbjasdlkbjasldkbjalksdbjaslkdbjaslkdbjaldjasabdaksldjbalksdjbasdglkajsdlgkjasdlkgjaskldgjasldkgjasdg"
    if not is_class(boundary_test, classnav_courses):
        print("Passed boundary test: single character input")
    else:
        print("Failed boundary test: single character input")
        all_passed = False

    if all_passed:
        print("\nAll tests passed.")
    else:
        print("\nSome tests failed.")
        sys.exit(1)
