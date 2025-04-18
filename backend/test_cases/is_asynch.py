import unittest

def validate_asynch_preference(class_data):
    """Parses class data and checks if asynchronous preference is enabled."""
    class_data = class_data.strip().split(';')

    # Ensure at least one entry exists and the last element follows "asynch:true/false"
    if not class_data or ':' not in class_data[-1]:
        return False  # Invalid format

    asynch_info = class_data[-1].strip().split(':')
    
    # Ensure valid key-value format
    if len(asynch_info) != 2 or asynch_info[0].strip() != "asynch":
        return False  

    return asynch_info[1].strip().lower() == "true"  # Convert to boolean


class TestAsynchPreference(unittest.TestCase):
    # Correct Input Cases (Valid cases)
    def test_asynch_preference_enabled(self):
        """Correct input case: Valid 'asynch:true' format"""
        result = validate_asynch_preference("Intro to Programming;C S 2586;Fall 2026;asynch:true")
        self.assertTrue(result)

    def test_asynch_preference_disabled(self):
        """Correct input case: Valid 'asynch:false' format"""
        result = validate_asynch_preference("Data Structures;C S 8328;Fall 2027;asynch:false")
        self.assertFalse(result)

    # Boundary Cases (Extreme valid inputs)
    def test_asynch_with_extra_spaces(self):
        """Boundary case: Extra spaces around the key-value pair"""
        result = validate_asynch_preference("Machine Learning;C S 3020;Fall 2025;   asynch:  true  ")
        self.assertTrue(result)

    # Edge Cases (Uncommon but possible inputs)
    def test_missing_asynch_entry(self):
        """Edge case: Missing 'asynch' entry"""
        result = validate_asynch_preference("Linear Algebra;MATH 1256;Spring 2025;")
        self.assertFalse(result)

    def test_malformed_asynch_entry(self):
        """Edge case: Incorrect key name 'async' instead of 'asynch'"""
        result = validate_asynch_preference("Physics;PHYS 9876;Fall 2025;async:yes")
        self.assertFalse(result)

    def test_invalid_asynch_value(self):
        """Edge case: Invalid value 'maybe' instead of 'true' or 'false'"""
        result = validate_asynch_preference("AI Ethics;C S 4444;Summer 2024;asynch:maybe")
        self.assertFalse(result)

    # Incorrect Cases (Completely wrong inputs)
    def test_completely_invalid_input(self):
        """Incorrect case: No structured format at all"""
        result = validate_asynch_preference("Just some random text")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
    