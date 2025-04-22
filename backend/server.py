from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/save', methods=['POST'])
def save_file():
    # Get data sent from frontend
    data = request.json.get("content", "")
    
    if not data:
        return jsonify({"error": "No data received"}), 400
    
    # Save data to a file
    with open("backend/data_extraction/user_data/courseData.txt", "a") as file:

        file.write(data + "\n")
    
    return jsonify({"message": "Data saved successfully!"})

if __name__ == '__main__':
    # Start the Flask server on localhost:5000
    app.run(debug=True)
