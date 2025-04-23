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
@app.route('/check-upload-status')
def check_upload():
    file_path = os.path.join(BACKEND_DIR, 'data_extraction/user_data/flowchart.pdf')
    exists = os.path.isfile(file_path)
    if exists:
        # If the file exists, run the filter script and return the filtered courses
        filtered_courses = run_filter_script()
        return jsonify({'uploaded': True, 'filtered_courses': filtered_courses})
    else:
        return jsonify({'uploaded': False})

def run_filter_script():
    # Run the data_filter.py script
    result = subprocess.run(['python', 'backend/ai_filtering/data_filter.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if result.returncode == 0:
        # Assuming the filtered courses are saved in 'filtered_courses.txt'
        filtered_courses_path = os.path.join(BACKEND_DIR, 'ai_filtering/filtered_courses.txt')
        if os.path.exists(filtered_courses_path):
            with open(filtered_courses_path, 'r') as file:
                return file.readlines()
        else:
            return [filtered_courses_path]
    else:
        return ["Error running filter script."]

if __name__ == '__main__':
    print("Serving frontend from:", FRONTEND_DIR)
    print("Serving backend  from:", BACKEND_DIR, "under /backend/")
    app.run(debug=True)