from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user

from.index import index_views

from App.controllers import (
    get_student_record
)

student_views = Blueprint('student_views', __name__, template_folder='../templates')

@student_views.route('/record/<student_id>', methods=['GET'])
@jwt_required()
def student_record(student_id):
    student = get_student_record(student_id=student_id)
    # reviews_count = len(reviews)
    return render_template('student.html',
                          student=student,
                           staff=jwt_current_user)