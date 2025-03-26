import unittest  # Import the unittest module for writing test cases
from gap_preference_validator import gapPreference  # Import the function to be tested

class TestGapPreference(unittest.TestCase):
    """
    Unit test class for testing the gapPreference function.
    """

    def test_valid_gap_time(self):
        """Test Case: Check that a valid integer time gap is accepted."""
        # A 60-minute (1 hour) gap should be valid
        self.assertTrue(gapPreference(60))

        # A 120-minute (2 hours) gap should be valid
        self.assertTrue(gapPreference(120))
    
    def test_invalid_non_integer_input(self):
        """Test Case: Ensure non-integer inputs are rejected."""
        # Strings should be rejected
        self.assertFalse(gapPreference("one hour"))

        # Float values should be rejected
        self.assertFalse(gapPreference(3.5))

        # None (no preference) should be rejected
        self.assertFalse(gapPreference(None))
    
    def test_boundary_multiple_hours_no_minutes(self):
        """Test Case: Ensure that time gaps in full hours (no extra minutes) are accepted."""
        # 6 hours (360 minutes) should be valid
        self.assertTrue(gapPreference(360))

        # 24 hours (1440 minutes) should be valid
        self.assertTrue(gapPreference(1440))
    
    def test_edge_negative_time(self):
        """Edge Case: Check that negative time inputs are rejected."""
        # A negative time gap should not be valid
        self.assertFalse(gapPreference(-60))
    
    def test_edge_time_over_a_day(self):
        """Edge Case: Ensure time gaps exceeding 24 hours are rejected."""
        # 1500 minutes (over 24 hours) should not be valid
        self.assertFalse(gapPreference(1500))
    
    def test_edge_no_preference_set(self):
        """Edge Case: Ensure None (no preference set) is handled correctly."""
        # If no gap preference is set (None), it should be rejected
        self.assertFalse(gapPreference(None))
        
# Run the test suite when executing the script
if __name__ == '__main__':
    unittest.main()