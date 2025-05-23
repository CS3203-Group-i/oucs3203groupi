import os
from flask import Flask, send_from_directory, request, jsonify, Blueprint
from flask_cors import CORS
import subprocess
from subprocess import Popen
from werkzeug.utils import secure_filename

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))    # …/oucs3203groupi/backend
project_root = os.path.dirname(script_dir)                  # …/oucs3203groupi
FRONTEND_DIR = os.path.join(project_root, 'frontend')       # …/oucs3203groupi/frontend
BACKEND_DIR  = script_dir                                   # …/oucs3203groupi/backend

# Making app
app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,    
    static_url_path=''            
)
CORS(app)

# Backend static blueprint
backend_bp = Blueprint(
    'backend_static',
    __name__,
    static_folder=BACKEND_DIR,
    static_url_path='/backend'
)
app.register_blueprint(backend_bp)

# Clears and old courseData (manual inputs) upon starting server
with open('backend/data_extraction/user_data/courseData.txt', 'w') as f:
    f.write("")

# Deletes old flowcharts
if os.path.exists('backend/data_extraction/user_data/flowchart.pdf'):
    os.remove('backend/data_extraction/user_data/flowchart.pdf')
 
# Clears old filtered information
with open('backend/ai_filtering/filtered_courses_manual.txt', 'w') as f:
    f.write("")
with open('backend/ai_filtering/filtered_courses_pdf.txt', 'w') as f:
    f.write("")

# Clears old ai results
with open('models/ai_result.txt', 'w') as f:
    f.write("")

# Routes
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Route for saving
@app.route('/save', methods=['POST'])
def save_file():
    data = request.json.get("content", "")
    if not data:
        return jsonify({"error": "No data received"}), 400

    # Can save user data (manual input)
    os.makedirs(os.path.join(BACKEND_DIR, "data_extraction", "user_data"), exist_ok=True)
    with open(os.path.join(BACKEND_DIR, "data_extraction", "user_data", "courseData.txt"), "a") as f:
        f.write(data + "\n")
    return jsonify({"message": "Data saved successfully!"})

# Route for uploading pdf
@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # verify file name is secure to prevent malicious uploads - Sarah
    filename = secure_filename(file.filename)
    if not filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Invalid file type, only PDF is allowed'}), 400

    if any(bad_extension in filename.lower() for bad_extension in ['.exe', '.bat', '.sh', '.php']):
        return jsonify({'error': 'This file type is not allowed'}), 400

    if file and file.filename.lower().endswith('.pdf'):
        save_path = os.path.join(BACKEND_DIR, "data_extraction", "user_data")
        os.makedirs(save_path, exist_ok=True)
        filename = "flowchart.pdf"
        file.save(os.path.join(save_path, filename))
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200

    return jsonify({'error': 'Invalid file type'}), 400

# Route for checking status of uploaded files for filter
@app.route('/check-upload-status')
def check_upload():
    pdf_path = os.path.join(BACKEND_DIR, 'data_extraction/user_data/flowchart.pdf')
    user_input_path = os.path.join(BACKEND_DIR, 'data_extraction/user_data/courseData.txt')

    # Check if the files exist
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
        'filtered_courses': [],  # Default t empty list
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
        # Paths
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
        # ased on inputted checkbox, run ai model
        # PDF takes priority over manual input
        if use_pdf:
            result = subprocess.run(['python', 'models/ai_model_request.py', '--input', 'pdf'], check=True)
        elif use_manual:
            result = subprocess.run(['python', 'models/ai_model_request.py', '--input', 'manual'], check=True)
        else:
            return jsonify({'error': 'No input type selected'}), 400
        
        # Check if the AI script ran successfully
        if result.returncode != 0:
            return jsonify({'error': 'AI model failed to run', 'stderr': result.stderr.decode()}), 500

        # Read in generated ai_result.txt file after running the AI script
        ai_result_path = 'models/ai_result.txt'
        if os.path.exists(ai_result_path):
            with open(ai_result_path, 'r') as result_file:
                ai_result = result_file.read()
            return ai_result
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route for running ai model
@app.route('/run-ai-model', methods=['POST'])
def run_ai():
    data = request.get_json()  # Get JSON data 
    
    # Get checkbox data (true/false) sent from frontend for pdf and manual
    # Both default false
    use_pdf = data.get('use_pdf', False)  
    use_manual = data.get('use_manual', False) 

    if not (use_pdf or use_manual):
        return jsonify({'error': 'Please select either PDF or Manual input.'}), 400
    
    # run ai model
    ai_result = run_ai_model(use_pdf, use_manual)
    return jsonify({'ai_result': ai_result}), 200

# Running app
if __name__ == '__main__':
    print("Serving frontend from:", FRONTEND_DIR)
    print("Serving backend  from:", BACKEND_DIR, "under /backend/")
    app.run(debug=True)