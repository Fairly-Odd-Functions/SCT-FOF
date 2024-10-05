from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user

from.index import index_views

from App.controllers import (
    get_student_record,
    get_student_reviews,
    get_average_rating
)

student_views = Blueprint('student_views', __name__, template_folder='../templates')

@student_views.route('/student_record', methods=['GET'])
@jwt_required()
def student_record():
    student_id = request.args.get('student_id')
    if len(student_id) == 9:
        student = get_student_record(student_id)
        if student:
            student_reviews = get_student_reviews(student_id)
            reviews_count = len(student_reviews)
            avg_rating = get_average_rating(student_id)
            return render_template('student.html',
                                   student=student,
                                   avg_rating=avg_rating,
                                   student_reviews=student_reviews,
                                   reviews_count=reviews_count,
                                   staff=jwt_current_user)
        else:
            flash("Student Not Found", "error")
            return redirect(request.referrer)
    else:
        flash("Invalid Student ID", "error")
        return redirect(request.referrer)

