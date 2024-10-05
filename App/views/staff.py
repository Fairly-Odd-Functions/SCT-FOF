from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user

from.index import index_views

from App.controllers import (
    create_staff,
    get_all_staffs,
    # get_reviews,
    get_all_staffs_json,
    jwt_required
)

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

@staff_views.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    # reviews = get_reviews(jwt_current_user.id)
    return render_template('staff.html',
                        #    staff_reviews = reviews,
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