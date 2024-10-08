from App.models import Student
from App.database import db

def get_all_students():
    return Student.query.all()

def get_all_students_json():
    students = Student.query.all()
    if not students:
        return []
    students = [student.get_json() for student in students]
    return students

def get_student_record(student_id):
    student = Student.query.get(student_id)
    return student

def get_student_record_json(student_id):
    student = Student.query.get(student_id)
    return student.get_json()

def get_student(student_id):
    return Student.query.get(student_id)

def check_student_email(email):
    return Student.query.filter_by(email=email).first()

def get_student_reviews(student_id):
    student = Student.query.get(student_id)
    if not student:
        return None
    reviews = [review for review in student.reviews]
    return reviews

def get_student_reviews_json(student_id):
    student = Student.query.get(student_id)
    if not student:
        return None
    reviews = [review.get_json() for review in student.reviews]
    return reviews