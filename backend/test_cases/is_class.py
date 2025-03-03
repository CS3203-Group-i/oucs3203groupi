# Loads the txt artifact file of all courses
def load_courses_from_file(filename):
    with open(filename, "r") as file:
        courses = {line.strip() for line in file if line.strip()}  # Removing empty lines
    return courses

# Calls the load courses function above on txt
cs_courses = load_courses_from_file("../data_extraction/data/extracted_classes.txt")

# Tests to check if class exists in known outcome
def is_class(course, course_set):
    return course in course_set  # true if exists and false if does not exist in txt

# Test cases
if __name__ == "__main__":
    #edge case
    empty_courses = set()
    assert is_class("C S 1213. Programming for Non-Majors with Python.", empty_courses) == False, "Failed edge case: Empty dataset"
    
    # Test cases with expected outcomes
    test_cases = [
        ("", False),  # Outcome should be false, Boundary condition for empty string
        ("C S 1213.  Programming for Non-Majors with Python.", True),  # Outcome should be true, it exists
        ("C S 3000.  Study of Procrastination.", False),  # Outcome should be false, it doesn't exist
        ("C S 2414.  Data Structures.", True),  # Outcome should be true, it exists
        ("C S 1111.  Study of Group Projects", False),  # Outcome should be false, it doesn't exist
    ]
    
    # Variable to check if all tests passed
    tests_all_passed = True

    # Loop that goes through each test case and checks it
    for course, expected in test_cases:
        result = is_class(course, cs_courses)
        if result == expected:
            print(f"Test passed for course: {course} Expected outcome {result} and got {result}")
        else:
            print(f"Test failed for course: {course} Expected outcome {expected}, but got {result}")
            # Changes all tests passed to false
            tests_all_passed = False
    
    # Conditional for final outcome of all tests passed variable
    if tests_all_passed:
        print("All tests passed.")
    else:
        print("All tests did NOT pass.")
        sys.exit(1)
