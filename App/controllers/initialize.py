import csv
from App.database import db
from flask import jsonify
from sqlalchemy.exc import IntegrityError
from App.models import Student, Review
from .staff import create_staff

def initialize():
    try:
        db.drop_all()
        db.create_all()

        # Create Staffs - Admin & Regular
        create_staff('Mr.', 'Bob', 'Bobberson', 'bob.bobberson@mail.com', True, 'bobpass', 0)
        create_staff('Mr.', 'Bobby', 'Butterbread', 'bobby.butterbread@mail.com', False, 'bobbypass', 0)

        # Students CSV
        with open("students.csv", encoding='unicode_escape') as csvfile:
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
                    except Exception as e:
                        print(f"ERROR: Adding Student: {row['firstname']} {row['lastname']}: {e}")
                else:
                    print(f"Student: {row['firstname']} {row['lastname']} Already Exists. Skipping...")
        db.session.commit()

        # Reviews CSV
        with open('reviews.csv', encoding='unicode_escape') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                review = Review(text=row['text'],
                                rating=row['rating'],
                                student_id=row['student_id'],
                                reviewer_id=row['reviewer_id'])
            db.session.add(review)
        db.session.commit()

    except IntegrityError as integrity_error:
        print(f"IntegrityError: {integrity_error}")
        return jsonify(error="Database Integrity Error Occurred"), 500
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify(error="An Error Occurred While Initializing Database"), 500

