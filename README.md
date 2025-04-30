# oucs3203groupi
Project for software engineering group i spring 2025 - OU class scheduler

Project Overview
This project is a Schedule Builder application that utilizes Python, BeautifulSoup, and Gemini to fetch and process class schedule data.

1. Install Python

Ensure you have Python installed. Download it from
https://www.python.org/downloads/
During installation, check the box ✅ "Add Python to PATH

2. Clone Repository

```
command: git clone https://github.com/CS3203-Group-i/oucs3203groupi
```

3. Create Virtual Enviroment

```sh
command: python3 -m venv venv
```

4. Activate Environment

Windows
```
command: .\.venv\Scripts\Activate
```
Linux
```
command: source venv/bin/activate
```

5. Add Dependencies

```
command: pip install -r requirements.txt
```

6. Branching

command git checkout -b "ticket name"
create a MR into main, with two peer reviewers
once accepted merge into main 

7. Activate Server

Inside of oucs3203groupi directory
```
command: python3 backend/server.py
```

8. Update api key

In models/ai_model_request.py:

Update gemini_api_key variable with own api key