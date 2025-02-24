import os
import requests

# Retrieve API key from secrets or environment variables
api_key = os.getenv("HF_TW_API")
if not api_key:
    raise ValueError("Hugging Face API key is missing. Set it as a secret or environment variable.")

# Define the API endpoint
model = "Qwen/Qwen2.5-Coder-32B-Instruct"
api_url = f"https://api-inference.huggingface.co/models/{model}"

# Headers including your API key
headers = {"Authorization": f"Bearer {api_key}"}

# Function to query the API
def generate_code(prompt):
    payload = {"inputs": prompt, "parameters": {"max_length": 512, "temperature": 0.7}}
    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    else:
        return f"Error {response.status_code}: {response.json()}"

# Example usage
prompt = """Given the following list of courses with their corresponding sections, times, and days, create an optimal schedule that ensures no time conflicts while taking exactly one section from each course. You can only take one section per course, and the sections must not overlap with each other. Put your final answer within \boxed{}​. Do not reason step by step.
Courses:
Math 3333:
Section 01: 10-11am T/TR
Section 02: 12-1pm M/W/F
Hist 1234:
Section 01: 10-11am T/TR
Section 02: 2-3pm M/W/F
CS 3203:
Section 01: 10-11am M/W/F
Section 02: 4-5pm M/W/F
ENGR 2002:
Section 01: 3-4pm M/W/F
Section 02: 9-10am T/TR
"""  

generated_code = generate_code(prompt)
print("Generated output: ", generated_code)
