from flask import Blueprint, jsonify
from App.controllers import initialize

index_views = Blueprint('index_views', __name__, template_folder='../templates')

"""Root"""
@index_views.route('/', methods=['GET'])
def index():
    return '<h1>Student Conduct Tracker - Fairly Odd Functions</h1>'

"""Initialize App"""
@index_views.route('/init', methods=['POST'])
def init():
    initialize()
    response_data = {"message": "Database Initialized!"}
    return jsonify(response_data), 200