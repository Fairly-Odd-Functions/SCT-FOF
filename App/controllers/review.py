from App.models import Review, Student
from App.database import db

def get_staff_reviews(reviewer_id):
    reviews = Review.query.filter_by(reviewer_id=reviewer_id).all()
    return reviews

def get__student_reviews(student_id):
    reviews = Review.query.filter_by(student_id=student_id).all()
    return reviews

def get_average_rating(student_id):
    reviews = Review.query.filter_by(student_id=student_id).all()

    if not reviews:
        return 0

    total_rating = sum(review.rating for review in reviews)
    average_rating = total_rating / len(reviews)

    return round(average_rating)
