import unittest
from professor_preference import validate_preference


class TestProfessorPreference(unittest.TestCase):
   def test_preference_valid(self):
       self.assertTrue(validate_preference("Yes"))
   def test_preference_edge(self):
       self.assertFalse(validate_preference("bruh"))




if __name__ == '__main__':
   unittest.main()
