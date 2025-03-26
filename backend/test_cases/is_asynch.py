import unittest

class TestAsynchPreference(unittest.TestCase):
    # Test if asynchPrefEnabled is true
    def test_asynch_preference_enabled(self):
        result = validate_asynch_preference("Intro to Programming;2586;Fall 2026;\nasynch:true")
        #print(result)
        self.assertTrue(result is True)

    # Test if asynchPrefEnabled is false
    def test_asynch_preference_disabled(self):
        result = validate_asynch_preference("Data Structures;58328;Fall 2027;/nasynch:false")
        #print(result)
        self.assertFalse(result is True)

def validate_asynch_preference(class_data):
    """Parses class data and checks if asynchronous preference is enabled."""
    class_data = class_data.strip().split(';')
    
    asynchBool = class_data[-1].strip().split(':')  # Extract the last element, which contains asynch info
    
    return asynchBool[1].strip().lower() == "true"  # Convert to boolean


if __name__ == '__main__':
    unittest.main()


