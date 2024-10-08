from App.database import db
from App.models import Review

# Add A Review
def add_review(student_id, text, rating, reviewer_id):
    student_review = Review(student_id=student_id, text=text, rating=rating, reviewer_id=reviewer_id)
    db.session.add(student_review)
    db.session.commit()
    return student_review