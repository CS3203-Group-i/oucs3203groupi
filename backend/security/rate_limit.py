# backend/student_athlete_route.py

import time
from flask import Blueprint, request, render_template

student_athlete_bp = Blueprint('student_athlete', __name__)

# Rate limiting state
studentathlete_last_call = {}

@student_athlete_bp.route('/student-athlete', methods=['GET'])
def student_athlete_page():
    user_ip = request.remote_addr
    now = time.time()
    if user_ip in studentathlete_last_call and now - studentathlete_last_call[user_ip] < 10:
        return "<h3>Too many requests. Try again in a few seconds.</h3>", 429

    studentathlete_last_call[user_ip] = now
    return render_template('AthleticSchedule.html')
