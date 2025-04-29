import requests
import os

# Flask server address
UPLOAD_URL = "http://127.0.0.1:5000/upload_pdf"

# Test files and expected result: True = should succeed, False = should fail
test_cases = {
    "sample.pdf": True,
    "exploit.php": False,
    "install.sh": False,
    "malware.exe": False,
    "report.pdf.exe": False,
    "script.js": False,
    "startup.bat": False,
}

# Create dummy files in a test_files/ folder
os.makedirs("test_files", exist_ok=True)
for filename in test_cases:
    with open(f"test_files/{filename}", "w") as f:
        f.write("Dummy content")

def upload_file(filename):
    with open(f"test_files/{filename}", "rb") as f:
        files = {"file": (filename, f)}
        response = requests.post(UPLOAD_URL, files=files)
    return response

def run_tests():
    print("Running Upload Security Tests...\n")
    for filename, should_succeed in test_cases.items():
        response = upload_file(filename)
        passed = (
            response.ok and should_succeed or
            not response.ok and not should_succeed
        )
        print(f"Test: {filename:30} | Expected: {'Success' if should_succeed else 'Failure'} | "
              f"Result: {'PASS' if passed else 'FAIL'}")
    print("\nDone.")

if __name__ == "__main__":
    run_tests()