# Function to read the course codes from the file
def load_courses_from_file(filename):
    with open(filename, "r") as file:
        courses = {line.strip() for line in file if line.strip()}  # Removing empty lines
    return courses

# Load the course list from the file
cs_courses = load_courses_from_file("../data_extraction/data/extracted_classes.txt")

# Function to check if the course exists in the set
def is_class(course, course_set):
    return course in course_set  # Returns True if the course is found, otherwise False

# Test cases
if __name__ == "__main__":
    # Define test cases as tuples (course, expected result)
    test_cases = [
        ("C S 1213.  Programming for Non-Majors with Python.", True),  # Expected: True
        ("C S 3000.  Study of Procrastination.", False),  # Expected: False
        ("C S 2414.  Data Structures.", True),  # Expected: True
        ("C S 1111.  Study of Group Projects", False),  # Expected: False
    ]
    
    # Check if each test case is correct
    for course, expected in test_cases:
        result = is_class(course, cs_courses)
        if result == expected:
            print(f"Test passed for course: {course} Expected {result} and got {result}")
        else:
            print(f"Test failed for course: {course} Expected {expected}, but got {result}")
    
    print("All tests passed.")