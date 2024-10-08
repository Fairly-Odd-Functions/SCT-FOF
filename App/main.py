import os, csv
from flask import Flask, render_template
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage


from App.database import init_db
from App.config import load_config


from App.controllers import (
    setup_jwt,
    add_auth_context
)

from App.models import db, Review, Student
from App.views import views, setup_admin

def add_views(app):
    for view in views:
        app.register_blueprint(view)

def create_app(overrides={}):
    app = Flask(__name__, static_url_path='/static')
    load_config(app, overrides)
    CORS(app)
    add_auth_context(app)
    photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)
    add_views(app)
    init_db(app)
    jwt = setup_jwt(app)
    setup_admin(app)
    @jwt.invalid_token_loader
    @jwt.unauthorized_loader
    def custom_unauthorized_response(error):
        return render_template('401.html', error=error), 401
    app.app_context().push()
    return app

def parse_students(filepath):
    with open(filepath, encoding='unicode_escape') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            student_id = row['student_id']
            email = row['email']
            existing_student_id = Student.query.filter_by(student_id=student_id).first()
            existing_student_email = Student.query.filter_by(email=email).first()
            
            if not existing_student_id and not existing_student_email:
                try:
                    student = Student(
                        student_id=row['student_id'],
                        firstname=row['firstname'],
                        lastname=row['lastname'],
                        email=row['email']
                    )
                    db.session.add(student)
                    print(f"Student: {student.firstname} {student.lastname} Added Successfully.")
                except Exception as e:
                    print(f"ERROR: Adding Student: {row['firstname']} {row['lastname']}: {e}")
            else:
                print(f"Student: {row['firstname']} {row['lastname']} Already Exists. Skipping...")
    db.session.commit()

def parse_reviews():
  with open('reviews.csv', encoding='unicode_escape') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    for row in reader:
      review = Review(text=row['text'],
                      rating=row['rating'],
                      student_id=row['student_id'],
                      reviewer_id=row['reviewer_id'])
      db.session.add(review)
    db.session.commit()