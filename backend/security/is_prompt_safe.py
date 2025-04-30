import re
import sys

# Function to check if a prompt is safe
def is_safe_prompt(prompt):
    
    # Check if the prompt is empty
    if isinstance(prompt, list):
        prompt = ' '.join(prompt)  

    # Checks for malicious patterns in prompt
    malicious_patterns = [
        r"<script.*?>.*?</script>",  # Detects <script> tags for XSS
        r"eval\((.*?)\)",            # Detects eval functions (code execution risk)
        r"(\bexec\(\))",             # Detects exec() function (code execution risk)
        r"\b(?:alert|prompt|document|window)\b",  # Detects potential XSS functions
        r"\b(?:rm|del|shutdown)\b",  # Detects potentially harmful system commands 
        r"\b(?:fuck|shit|bitch|asshole|damn)\b",  # Detects inappropriate language
        r"(\b(?:system|os\.system)\b)",  # Detects system calls (could be risky)
    ]
    
    # Loops through patterns to see if malicious prompt
    for pattern in malicious_patterns:
        # checks regex pattern in prompt
        if re.search(pattern, prompt, re.IGNORECASE):

            # Bad prompt, not safe
            print(f"Malicious pattern detected: {pattern}")
            return False  
    
    # Prompt most likely safe
    return True   

# Printing out if prompt is safe or not
def test_prompt(prompt):
    if is_safe_prompt(prompt):
        print("safe")
    else:
        print("unsafe")

# Takes in system input (prompt) from ai model request and tests to see if safe or not
if __name__ == "__main__":
    prompt = sys.argv[1:]
    test_prompt(prompt)
