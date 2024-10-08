from flask import Blueprint, jsonify, request

from App.controllers import (
    login
)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

"""Login"""
@auth_views.route('/login', methods=['POST'])
def login_action():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify(error='Email And Password Are Required'), 400

        token = login(data['email'], data['password'])
        if not token:
            return jsonify(error='Bad Email Or Password Given'), 401

        return jsonify(access_token=token)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify(error="An Error Occurred While Loggin In"), 500