from flask import Blueprint, jsonify, request
from flask_jwt_extended import unset_jwt_cookies

from App.controllers import (
    login
)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

'''
Page/Action Routes
'''    
@auth_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users() # type: ignore
    return render_template('users.html', users=users)

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")

"""Login"""
@auth_views.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify(error='Email And Password Are Required'), 400

        token = login(data['email'], data['password'])

        if not token:
            return jsonify({"error": "Bad email or password given"}), 401

        return jsonify(access_token=token), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify(error="An Error Occurred While Logging In"), 500

"""Logout"""
@auth_views.route('/logout', methods=['POST'])
def logout_action():
    try:
        response = jsonify(message="Logged Out Successfully")
        unset_jwt_cookies(response)
        return response, 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify(error="An Error Occurred While Logging Out"), 500
