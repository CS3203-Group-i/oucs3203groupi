import re
from pathlib import Path

# Path to the extracted schedule data
data_path = Path("backend/data_extraction/data/extracted_classnav.txt")

# Test inputs to verify
test_queries = ["MATH 3113", "A HI 5823"]

def normalize_query(query):
    """Split and normalize course input."""
    parts = query.strip().split()
    course = parts[-1]
    subject = " ".join(parts[:-1])
    return subject.upper(), course

def load_data(filepath):
    """Load schedule lines from the data file."""
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.readlines()

def run_tests():
    print("🔍 Running Regenerate Schedule Test Case...\n")
    try:
        lines = load_data(data_path)
    except Exception as e:
        print(f"❌ Error loading data file: {e}")
        return

    all_passed = True

    for query in test_queries:
        subject, course = normalize_query(query)
        pattern = re.compile(rf"\|\s*{re.escape(subject)}\s*\|\s*{re.escape(course)}\s*\|")
        match_found = any(pattern.search(line) for line in lines)

        if match_found:
            print(f"✅ PASS: Match found for '{query}'")
        else:
            print(f"❌ FAIL: No match found for '{query}'")
            all_passed = False

    print("\n🎯 Test Result:", "✅ ALL PASSED" if all_passed else "❌ SOME FAILED")

if __name__ == "__main__":
    run_tests()
