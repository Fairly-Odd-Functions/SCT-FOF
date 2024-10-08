from flask import Blueprint, jsonify, request

from App.controllers import (
    login
)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

"""Login"""

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

@auth_views.route('/login', methods=['POST'])
def login_action():
    try:
        data = request.form
        token = login(data['email'], data['password'])
        if not token:
            return jsonify(error='Bad Email Or Password Given'), 401

        return jsonify(access_token=token)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify(error="An Error Occurred While Loggin In"), 500