import os
from flask import Flask, send_from_directory, request, jsonify, Blueprint
from flask_cors import CORS
import subprocess
from subprocess import Popen

# ─── Prep paths ────────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))    # …/oucs3203groupi/backend
project_root = os.path.dirname(script_dir)                  # …/oucs3203groupi
FRONTEND_DIR = os.path.join(project_root, 'frontend')       # …/oucs3203groupi/frontend
BACKEND_DIR  = script_dir                                   # …/oucs3203groupi/backend

# ─── Create app ───────────────────────────────────────────────────────────────
app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,   # serve frontend/ at /
    static_url_path=''            # so /index.html, /img/…, /js/… all come from frontend/
)
CORS(app)

# ─── Blueprint to serve backend/ at /backend/… ─────────────────────────────────
backend_bp = Blueprint(
    'backend_static',
    __name__,
    static_folder=BACKEND_DIR,
    static_url_path='/backend'
)
app.register_blueprint(backend_bp)

# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/save', methods=['POST'])
def save_file():
    data = request.json.get("content", "")
    if not data:
        return jsonify({"error": "No data received"}), 400

    os.makedirs(os.path.join(BACKEND_DIR, "data_extraction", "user_data"), exist_ok=True)
    with open(os.path.join(BACKEND_DIR, "data_extraction", "user_data", "courseData.txt"), "a") as f:
        f.write(data + "\n")
    return jsonify({"message": "Data saved successfully!"})

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.lower().endswith('.pdf'):
        save_path = os.path.join(BACKEND_DIR, "data_extraction", "user_data")
        os.makedirs(save_path, exist_ok=True)
        filename = "flowchart.pdf"
        file.save(os.path.join(save_path, filename))
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/check-upload-status')
def check_upload():
    pdf_path = os.path.join(BACKEND_DIR, 'data_extraction/user_data/flowchart.pdf')
    user_input_path = os.path.join(BACKEND_DIR, 'data_extraction/user_data/courseData.txt')

    pdf_exists = os.path.isfile(pdf_path)
    user_input_exists = os.path.isfile(user_input_path)

    user_input_lines = []
    if user_input_exists:
        with open(user_input_path, 'r') as file:
            user_input_lines = file.readlines()

    response = {
        'pdf_uploaded': pdf_exists,
        'user_input_uploaded': user_input_exists,
        'user_input_lines': user_input_lines,
        'filtered_courses': [],  # Default to empty list
    }

    # Run the filter if either PDF or manual input exists
    if pdf_exists or user_input_exists:
        filtered_courses = run_filter_script()
        response['filtered_courses'] = filtered_courses

    return jsonify(response)

def run_filter_script():
    # Run the data_filter.py script
    result = subprocess.run(['python', 'backend/ai_filtering/data_filter.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if result.returncode == 0:
        # Define the paths for the filtered course files
        filtered_courses_pdf_path = os.path.join(BACKEND_DIR, 'ai_filtering/filtered_courses_pdf.txt')
        filtered_courses_manual_path = os.path.join(BACKEND_DIR, 'ai_filtering/filtered_courses_manual.txt')

        # Check if either of the filtered course files exists
        if os.path.exists(filtered_courses_pdf_path):
            with open(filtered_courses_pdf_path, 'r') as file:
                return file.readlines()
        elif os.path.exists(filtered_courses_manual_path):
            with open(filtered_courses_manual_path, 'r') as file:
                return file.readlines()
        else:
            return ["No filtered course files found."]
    else:
        return ["Error running filter script."]

def run_ai_model(use_pdf, use_manual):
    try:
        # Based on the selected checkboxes, we choose the model argument
        if use_pdf:
            result = subprocess.run(['python', 'models/ai_model_request.py', '--input', 'pdf'], check=True)
            #print("HELP")
        elif use_manual:
            result = subprocess.run(['python', 'models/ai_model_request.py', '--input', 'manual'], check=True)
        else:
            return jsonify({'error': 'No input type selected'}), 400
        
        # Check if the AI script ran successfully
        if result.returncode != 0:
            return jsonify({'error': 'AI model failed to run', 'stderr': result.stderr.decode()}), 500

        # Read the generated ai_result.txt file after running the AI script
        ai_result_path = 'models/ai_result.txt'
        if os.path.exists(ai_result_path):
            with open(ai_result_path, 'r') as result_file:
                ai_result = result_file.read()
            return ai_result
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/run-ai-model', methods=['POST'])
def run_ai():
    data = request.get_json()  # Get JSON data sent from the frontend
    
    # Get checkbox data (true/false) sent from frontend
    use_pdf = data.get('use_pdf', False)  # Default to False if not present
    use_manual = data.get('use_manual', False)  # Default to False if not present

    if not (use_pdf or use_manual):
        return jsonify({'error': 'Please select either PDF or Manual input.'}), 400
    
    # Only run the AI model here, not in the check-upload-status route
    ai_result = run_ai_model(use_pdf, use_manual)
    #print("ai result is: {ai_result}")
    #print(ai_result)
    return jsonify({'ai_result': ai_result}), 200


if __name__ == '__main__':
    print("Serving frontend from:", FRONTEND_DIR)
    print("Serving backend  from:", BACKEND_DIR, "under /backend/")
    app.run(debug=True)