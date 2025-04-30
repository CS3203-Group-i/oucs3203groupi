# Checks if contains emojis
# Checks if contains invalid symbols !?@
# Checks if no prompt (empty, edge case)
# Checks if longer than 10000 characters (boundary)

import unittest
import re
import sys

def is_valid_prompt(text):
    # Test for empty prompt
    if not text: 
        return "Not valid, no prompt such that it's empty."

    # Test for boundary case of too long of preferences
    if len(text) > 10000:
        return "Not valid, too many characters."

    # Test for invalid symbols
    if re.search(r"[!?@]", text):  # Check for invalid symbols
        return "Not valid, contains invalid symbols."

    if any(ord(char) > 127 for char in text):  # Check for emojis (non-ASCII)
        return "Not valid, contains emoji."

    return "Valid."

class TestPromptValidation(unittest.TestCase):

    # Edge case
    def test_empty(self):
        self.assertEqual(is_valid_prompt(""), "Not valid, no prompt such that it's empty.")

    # Boundary case
    def test_large_characters(self):
        self.assertEqual(is_valid_prompt("A" * 10000), "Not valid, too many characters.")

    # Test correct input
    def test_correct(self):
        self.assertEqual(is_valid_prompt("I want only afternoon classes."), "Valid.")

    # Test incorrect input
    def test_emoji(self):
        self.assertEqual(is_valid_prompt("No morning classes 😊"), "Not valid, contains emoji.")

    # Test another incorrect input
    def test_invalid_symbols(self):
        self.assertEqual(is_valid_prompt("Hello!&*#()"), "Not valid, contains invalid symbols.")

# If this script is called directly (not imported)
if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = ' '.join(sys.argv[1:])  # Support multi-word prompts
        print(is_valid_prompt(prompt))   # Output the result for subprocess capture
    else:
        unittest.main()