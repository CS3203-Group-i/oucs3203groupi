import unittest
from datetime import datetime

# Constants
START_BOUND = datetime.strptime("05:00", "%H:%M")
END_BOUND = datetime.strptime("21:00", "%H:%M")

# Core validation function
def is_valid_practice_time(start, end):
    try:
        start_dt = datetime.strptime(start, "%H:%M")
        end_dt = datetime.strptime(end, "%H:%M")

        # Check chronological order
        if start_dt >= end_dt:
            return False

        # Check if within 5:00 AM to 9:00 PM
        if start_dt < START_BOUND or end_dt > END_BOUND:
            return False

        return True
    except Exception:
        return False

class TestManualPracticeTimes(unittest.TestCase):

    # ✅ Normal valid case
    def test_valid_range(self):
        self.assertTrue(is_valid_practice_time("08:00", "10:00"))

    # End time before start time
    def test_invalid_time_order(self):
        self.assertFalse(is_valid_practice_time("12:00", "11:00"))

    # Start equals end
    def test_same_time(self):
        self.assertFalse(is_valid_practice_time("14:30", "14:30"))

    # Outside lower bound (before 5 AM)
    def test_start_before_5am(self):
        self.assertFalse(is_valid_practice_time("04:45", "06:00"))

    # Outside upper bound (after 9 PM)
    def test_end_after_9pm(self):
        self.assertFalse(is_valid_practice_time("20:30", "21:30"))

    # Edge case: exactly on bounds
    def test_exact_bounds(self):
        self.assertTrue(is_valid_practice_time("05:00", "21:00"))

    # Bad format
    def test_invalid_format(self):
        self.assertFalse(is_valid_practice_time("5 PM", "6 PM"))

    # Empty input
    def test_empty_input(self):
        self.assertFalse(is_valid_practice_time("", ""))

if __name__ == "__main__":
    unittest.main()
