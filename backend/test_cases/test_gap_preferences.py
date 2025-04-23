import unittest
from gap_preference_validator import gapPreference  # This is your validation logic

def validate_gap_preference(class_data):
    """
    Parses class data and checks if the gap preference is valid.
    Expects format: 'CourseName;ID;Term;GapPref:60'
    """
    try:
        class_data = class_data.strip().split(';')
        gap_info = class_data[-1].strip().split(':')  # e.g., ['GapPref', '60']

        if gap_info[0].strip().lower() == 'gappref':
            gap_value = int(gap_info[1].strip())
            return gapPreference(gap_value)
        else:
            return False
    except (IndexError, ValueError):
        return False


class TestGapPreference(unittest.TestCase):
    # Base case: typical valid input
    def test_valid_gap_time(self):
        result = validate_gap_preference("Intro to Programming;2586;Fall 2026;GapPref:60")
        self.assertTrue(result)

    # Fail case: not a multiple of 60
    def test_invalid_gap_time(self):
        result = validate_gap_preference("CS101;1234;Spring 2025;GapPref:45")
        self.assertFalse(result)

    # Fail case: gap value is not an integer
    def test_invalid_non_integer(self):
        result = validate_gap_preference("CS101;1234;Spring 2025;GapPref:sixty")
        self.assertFalse(result)

    # Fail case: missing gap preference altogether
    def test_missing_gap_pref(self):
        result = validate_gap_preference("CS101;1234;Spring 2025")
        self.assertFalse(result)

    # Fail case: gap value too large (exceeds 24 hours)
    def test_gap_too_large(self):
        result = validate_gap_preference("CS101;1234;Spring 2025;GapPref:1500")
        self.assertFalse(result)

    # Edge case: upper boundary of allowed value (exactly 24 hours)
    def test_gap_upper_limit(self):
        result = validate_gap_preference("CS101;1234;Spring 2025;GapPref:1440")
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
