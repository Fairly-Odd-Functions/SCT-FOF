from App.models import Review, Student
from App.database import db

def get_reviews(reviewer_id):
    reviews = Review.query.filter_by(reviewer_id=reviewer_id).all()
    return reviews