from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/input-classes')
def input_classes():
    return render_template('base.html')  # Example template

@app.route('/submit-flowchart') # flowchart pdf upload
def submit_flowchart():
    return render_template('submit_flowchart.html')

@app.route('/campus-resources') # campus resources
def campus_resources():
    return render_template('campus_resources.html')

if __name__ == '__main__':
    app.run(debug=True)