from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user

from.index import index_views

from App.controllers import (
    create_staff,
    add_student,
    add_review,
    get_student_record,
    get_all_staffs,
    get_staff_reviews,
    get_student_reviews,
    get_all_staffs_json,
    jwt_required
)

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

@staff_views.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    reviews = get_staff_reviews(jwt_current_user.id)
    students_reviewed = len(reviews)
    return render_template('staff.html',
                           staff_reviews=reviews,
                           students_reviewed=students_reviewed,
                           staff=jwt_current_user)

@staff_views.route('/add_student', methods=['POST'])
@jwt_required()
def add_student_record():
    data = request.form
    student_id = data['student_id']
    student_firstname = data['firstname']
    student_lastname = data['lastname']
    student_email = data['email']

    if len(student_id) == 9:
        new_student = add_student(student_id=student_id, 
                                firstname=student_firstname, 
                                lastname=student_lastname,
                                email=student_email)
        if new_student is None:
            flash("A Student That ID Or Email Already Exists!", "error")
            return redirect(request.referrer)
        
        else:
            flash("Student Added Successfully!", "success")
            return redirect(request.referrer)
    else:
        flash("Invalid Student ID!", "error")
        return redirect(request.referrer)

@staff_views.route('/create_staff', methods=['POST'])
@jwt_required()
def add_staff_account():
    # prefix, firstname, lastname, email, is_admin, password, created_by_id
    data = request.form
    staff_prefix = data['prefix']
    staff_firstname = data['firstname']
    staff_lastname = data['lastname']
    staff_email = data['email']
    is_admin = 'is_admin' in data and data['is_admin'] == 'on'
    password = data['password']
    new_staff = create_staff(prefix=staff_prefix,
                             firstname=staff_firstname,
                             lastname=staff_lastname,
                             email=staff_email,
                             is_admin=is_admin,
                             password = password,
                             created_by_id = jwt_current_user.id)

    if new_staff is None:
        flash("A Staff With That Email Already Exists!", "error")
        return redirect(request.referrer)

    else:
        flash("Staff Account Created Successfully!", "success")
        return redirect(request.referrer)

@staff_views.route('/review_student', methods=['POST'])
@jwt_required()
def review_student():
# text, rating, student_id, reviewer_id
    data = request.form
    text = data['review-text']
    rating = data['rating']
    student_id = data['student-id']
    new_review = add_review(
                    text=text,
                    rating=rating,
                    student_id=student_id,
                    reviewer_id=jwt_current_user.id)
    flash("Review Added!", "success")
    return redirect(request.referrer)

@staff_views.route('/view_student_reviews', methods=['GET'])
@jwt_required()
def view_student_reviews():
    student_id = request.args.get('student-id')
    student = get_student_record(student_id)
    reviews = get_student_reviews(student_id)
    return render_template('stu_reviews.html',
                           student=student,
                           student_reviews=reviews,
                           staff=jwt_current_user)

@staff_views.route('/view_staff_reviews', methods=['GET'])
@jwt_required()
def view_staff_reviews():
    reviews = get_staff_reviews(jwt_current_user.id)
    return render_template('sta_reviews.html',
                           staff_reviews=reviews,
                           staff=jwt_current_user)

@staff_views.route('/staffs', methods=['GET'])
def get_staff_page():
    staffs = get_all_staffs()
    return render_template('staffs.html', staffs=staffs)

@staff_views.route('/staffs', methods=['POST'])
def create_staff_action():
    data = request.form
    flash(f"staff {data['staffname']} created!")
    create_staff(data['staffname'], data['password'])
    return redirect(url_for('staff_views.get_staff_page'))

@staff_views.route('/api/staffs', methods=['GET'])
def get_staffs_action():
    staffs = get_all_staffs_json()
    return jsonify(staffs)

@staff_views.route('/api/staffs', methods=['POST'])
def create_staff_endpoint():
    data = request.json
    staff = create_staff(data['staffname'], data['password'])
    return jsonify({'message': f"staff {staff.staffname} created with id {staff.id}"})

@staff_views.route('/static/staffs', methods=['GET'])
def static_staff_page():
  return send_from_directory('static', 'static-staff.html')