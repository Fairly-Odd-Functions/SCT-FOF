from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_staff as jwt_current_staff

from.index import index_views

from App.models import Review #Needed to call get_json() I assume

from App.controllers import (
    create_staff,
    get_all_staffs,
    get_all_staffs_json,
    get_student_record,
    get_student_record_json,
    get_student_reviews,
    add_student, #To be included in admin.py imports
    add_review,  #To be included in admin.py imports
    jwt_required
)

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

# POSTMAN METHOD #2 -  CREATE A STAFF ACCOUNT
@staff_views.route('/admins', methods=['POST'])
def create_staff_action():
    data = request.form

    if not data['prefix'] or not data['firstname'] or not data['lastname'] or not data['email']:
        return jsonify({"erorr": "Missing Required Fields"}),400

    create_staff(data['prefix'],
                 data['firstname'],
                 data['lastname'],
                 data['email'],
                 True,                  # is_admin will alway be True if user is logged in as admin
                 data['created_by_id'], # !! I am not sure how this field will be obtained from request.form aka <form>...</form>
                 data['password'],)
    
    flash(f"Staff Account For {data['prefix']} {data['firstname']} {data['lastname']} Created!")
    #return render_template('staff_profile.html')

# POSTMAN METHOD #3 -  ADDS A STUDENT RECORD
@staff_views.route('/staffs', methods=['POST'])
def add_student_action():
    data = request.form
    
    if not data['student_id'] or not data['firstname'] or not data['lastname'] or not data['email']:
        return jsonify({"erorr": "Missing Required Fields"}),400
    
    new_student = add_student(data['student_id'],
                              data['firstname'],
                              data['lastname'],
                              data['email'])
    
    if new_student:
        return jsonify({"message": f"A Record Has Been Made For Student: {data['firstname']} {data['lastname']}."}),201
    else:
        return jsonify({"error": "ERROR: A Student With That ID Already Exists In The Database!"}),409

# POSTMAN METHOD #4 - ADDS A REVIEW TO A STUDENT    Note: ADDED ADJUSTMENTS TO REVIEW MODEL FOR RATING FEATURE
@staff_views.route('/staffs', methods=['PUT'])
def add_student_review_action():
    data = request.form

    if not data['student_id'] or not data['text'] or not data['rating'] or not data['reviewer_id']:
        return jsonify({"error": "Missing Required Fields"}),400
    
    new_review = add_review(int(data['student_id']),
                            data['text'],
                            int(data['rating']),
                            int(data['reviewer_id']))
                    
    if new_review:
        student = get_student_record(data['student_id'])
        return jsonify({"message": f"Review Uploaded To Student With ID: {data['student_id']} ({student.firstname} {student.lastname}) Successfully!"}),200
    else:
        return jsonify({"error": f"ERROR: Student With ID {data['student_id']} Does Not Exist"}),400
    
# POSTMAN METHOD #5 - LIST ALL REVIEWS FOR SPECIFIED STUDENT
@staff_views.route('/staffs', methods=['GET'])
def view_student_reviews_action():
    student_id = request.form.get('student_id')

    if not student_id:
        return jsonify({"error": "Missing Required Fields"}), 400

    reviews = get_student_reviews()
    if reviews:
        student_reviews = [reviews.get_json() for review in reviews]
        return jsonify({"message": student_reviews}), 200
    
        #return render_template('student_reviews.html', reviews=reviews)
    else:
        return jsonify({"message": "ERROR: Student With ID {student_id} Does Not Exist"}),404

# POSTMAN METHOD #6 - SEARCHES FOR SPECIFIC STUDENT
@staff_views.route('/staffs/<student_id>', methods=['GET'])
def search_student_action(student_id):
  
    student_record = get_student_record_json(student_id)

    if student_record:
        return jsonify({"student": student_record}),200
    else:
        return jsonify({"message": f"ERROR: Student With ID {student_id} Does Not Exist"}),404


'''
Extra Routes
'''



'''
Example Routes by Sir
'''

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