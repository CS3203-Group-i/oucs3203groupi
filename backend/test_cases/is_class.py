# Function to read the course codes from the file
def load_courses_from_file(filename):
    with open(filename, "r") as file:
        courses = {line.strip() for line in file if line.strip()}  # Removing empty lines
    return courses

# Load the course list from the file
cs_courses = load_courses_from_file("extracted_classes.txt")

# Function to check if the course exists in the set
def is_class(course, course_set):
    return course in course_set  # Returns True if the course is found, otherwise False

# Test cases
if __name__ == "__main__":
    print(is_class("C S 1213.  Programming for Non-Majors with Python.", cs_courses))  # Expected: True (if it's in the file)
    print(is_class("C S 3000.  Study of Procrastination.", cs_courses))  # Expected: False (if it's not in the file)
    print(is_class("C S 2813.  Discrete Structures.", cs_courses))  # Expected: True (if it's in the file)
    print(is_class("C S 1111.  Study of Grooup Projects", cs_courses))  # Expected: False (if it's not in the file)

    
