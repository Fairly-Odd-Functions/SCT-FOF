from App.database import db
from App.models import Student, Review

# Get Student
def get_student(student_id):
    return Student.query.get(student_id)

# Get Student (JSON)
def get_student_json(student_id):
    student = Student.query.get(student_id)
    if not student:
        return []
    return student.get_json()

# Get Student Reviews
def get_student_reviews(student_id):
    reviews = Review.query.filter_by(student_id=student_id).all()
    if not reviews:
        return None
    return reviews

# Get Student Reviews (JSON)
def get_student_reviews_json(student_id):
    reviews = Review.query.filter_by(student_id=student_id).all()
    if not reviews:
        return []
    return [review.get_json() for review in reviews]

# Add A Student
def add_student (student_id, firstname, lastname, email):
    try:
        existing_student = get_student(student_id)
        if existing_student is not None:
            return None

        new_student = Student(student_id, firstname=firstname, lastname=lastname, email=email)
        db.session.add(new_student)
        db.session.commit()
        return new_student

    except Exception as e:
        print(f"Error While Adding Student: {e}")
        db.session.rollback()
        return None