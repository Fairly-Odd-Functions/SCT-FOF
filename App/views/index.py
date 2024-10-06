from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify
from App.controllers import create_staff, initialize

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index_page():
    return render_template('index.html')

# POSTMAN METHOD #1 -  CREATE AND INITIALIZE THE DATABASE
@index_views.route('/init', methods=['POST']) # ~was originally GET chnaged to POST
def init():
    initialize()
    return jsonify(message='Database initialized!')

# @index_views.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({'status':'healthy'})