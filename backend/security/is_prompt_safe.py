import re
import sys

def is_safe_prompt(prompt):
    # Ensure prompt is a string, in case it comes as a list
    if isinstance(prompt, list):
        prompt = ' '.join(prompt)  # Join list elements into a single string

    malicious_patterns = [
        r"<script.*?>.*?</script>",  # Detects <script> tags for XSS
        r"eval\((.*?)\)",            # Detects eval functions (code execution risk)
        r"(\bexec\(\))",             # Detects exec() function (code execution risk)
        r"\b(?:alert|prompt|document|window)\b",  # Detects potential XSS functions
        r"\b(?:rm|del|shutdown)\b",  # Detects potentially harmful system commands 
        r"\b(?:fuck|shit|bitch|asshole|damn)\b",  # Detects inappropriate language
        r"(\b(?:system|os\.system)\b)",  # Detects system calls (could be risky)
    ]
    
    for pattern in malicious_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            print(f"Malicious pattern detected: {pattern}")
            return False  # Unsafe prompt
    
    return True  # Safe prompt  

def test_prompt(prompt):
    if is_safe_prompt(prompt):
        print("safe")
    else:
        print("unsafe")

if __name__ == "__main__":
    prompt = sys.argv[1:]
    test_prompt(prompt)
