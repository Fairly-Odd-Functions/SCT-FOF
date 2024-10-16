from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user as jwt_current_user

from App.controllers import (
    create_staff,
    get_student,
    get_student_json,
    add_student,
    add_review,
    get_student_reviews_json,
    jwt_required
)

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

"""Create Staff""" # Admin Staff vs Regular Staff
@staff_views.route('/create_staff', methods=['POST'])
@jwt_required()
def create_staff():
    try:
        current_staff = jwt_current_user
        if not current_staff.is_admin:
            return jsonify(error="Not Authorized To Create Staff Members. Admin Staff Only."), 403

        data = request.get_json()
        prefix = data.get('prefix')
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        email = data.get('email')
        is_admin = data.get('is_admin')
        password = data.get('password')
        created_by_id = data.get('created_by_id')

        if not firstname or not lastname or not email or password is None:
            return jsonify(error="All Fields Are Required"), 400

        new_staff = create_staff(prefix, firstname, lastname, email, is_admin, password, created_by_id)
        if new_staff is None:
            return jsonify(error="Failed To Create Staff Member Or Staff Member Already Exists."), 400

        message=f'Staff: {new_staff.prefix} {new_staff.firstname} {new_staff.lastname} Created By Admin Staff: {current_staff.prefix} {current_staff.firstname} {current_staff.lastname} Successfully!'
        return jsonify(message=message), 201

    except Exception as e:
        print(f"Error while creating staff: {e}")
        return jsonify(error="An error occurred while creating the staff member."), 500

"""Add Student""" # Requirement #1
@staff_views.route('/add_student', methods=['POST'])
def add_student():
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        email = data.get('email')

        if not student_id or not firstname or not lastname or not email:
            return jsonify(error="All Fields Are Required To Add Student"), 400

        new_student = add_student(student_id, firstname, lastname, email)
        if new_student is None:
            return jsonify(error="Failed To Add Student Or Student Already Exists."), 400

        message = f'Student: {new_student.firstname} {new_student.lastname} With Student ID: {new_student.student_id} Added Successfully!'
        return jsonify(message=message), 201

    except Exception as e:
        print(f"Error While Adding Student: {e}")
        return jsonify(error="An Error Occurred While Adding The New Student."), 500

"""Review Student""" # Requirement #2
@staff_views.route('/review/<int:student_id>', methods=['POST'])
@jwt_required()
def review_student(student_id):
    try:
        reviewer_id = jwt_current_user.id

        data = request.get_json()
        text = data.get('text')
        rating = data.get("rating")

        if not text or not rating:
            return jsonify(error="Text And Rating Are Required."), 400

        new_review = add_review(student_id, text, rating, reviewer_id)
        if not new_review:
            return jsonify(error="Failed To Add New Review."), 500
        
        message = f'Review Made By {jwt_current_user.prefix} {jwt_current_user.firstname} {jwt_current_user.lastname} Added Successfully To Student With ID: {student_id}'
        return jsonify(message=message), 201

    except Exception as e:
        print(f"Error: {e}")
        return jsonify(error="An Error Occurred While Reviewing The Student."), 500

"""Search Student""" # Requirement #3
@staff_views.route('/search/<int:student_id>', methods=['GET'])
def search_student(student_id):
    try:
        student = get_student_json(student_id)
        if not student:
            return jsonify(error="Student Not Found"), 404

        return jsonify(student), 200

    except Exception as e:
        print(f"Error Searching Student With ID {student_id}: {e}")
        return jsonify(error=f"An Error Occurred While Searching For Student With ID:{student_id}"), 500

"""View Student Reviews""" # Requirement #4
@staff_views.route('/list_reviews/<int:student_id>', methods=['GET'])
def list_student_reviews(student_id):
    try:
        student = get_student(student_id)
        if not student:
            return jsonify(error=f'Student With ID {student_id} Not Found'), 404

        student_reviews = get_student_reviews_json(student_id)
        return jsonify(student_reviews), 200 # Extra Support!

    except Exception as e:
        print(f"Error: {e}")
        return jsonify(error=f"An Error Occurred While Getting Reviews For Student With ID:{student_id}"), 500

#---------------------------------------------------------------------------------
"""Add Student - Invalid ID"""
@staff_views.route('/add_student', methods=['POST'])
def add_student_invalid_id():
    try:
        data = request.get_json()
        student_id = data.get('student_id')

        if len(student_id) != 9 or student_id in ['999999999', '000000000']:
            return jsonify({'message': f"Invalid Student ID {student_id}"}), 406
        
    except Exception as e:
        print(f"Error While Adding Student: {e}")
        return jsonify(error="An Error Occurred While Adding The New Student."), 500

"""List Student Reviews - Bad ID"""
@staff_views.route('/list_reviews/<int:bad_student_id>', methods=['GET'])
def list_student_reviews_bad_id(bad_student_id):
    try:
        not_student = get_student(bad_student_id)
        if not not_student:
            return jsonify(error=f'Student With ID {bad_student_id} Does Not Exist'), 400

    except Exception as e:
        print(f"Error: {e}")
        return jsonify(error=f"An Error Occurred While Getting Reviews For Student With ID:{bad_student_id}"), 500

"""List Student Reviews - Empty (e.g New Student)"""
@staff_views.route('/list_reviews/<int:student_id>', methods=['GET'])
def list_student_reviews(student_id):
    try:
        student_reviews = get_student_reviews_json(student_id)
        if not student_reviews:
            return jsonify({'message': f"ERROR: Student With ID {student_id} Does Not Have Any Reviews Currently."}), 400

    except Exception as e:
        print(f"Error: {e}")
        return jsonify(error=f"An Error Occurred While Getting Reviews For Student With ID:{student_id}"), 500

#---------------------------------------------------------------------------------