from App.database import db

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  #~added rating feature
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    reviewer = db.relationship('Staff', backref='reviewed', lazy=True)

    def __init__(self, text, rating, student_id, reviewer_id):  #~adjusted for rating feature
      self.text = text
      self.rating = rating
      self.student_id = student_id
      self.reviewer_id = reviewer_id

    def get_json(self): #~adjusted for rating feature
        return{
            'student_id': self.student_id,
            'text': self.text,
            'rating': self.rating,
            'reviewer': f"{self.reviewer.prefix} {self.reviewer.firstname} {self.reviewer.lastname}"
        }

    def __repr__(self): #~adjusted for rating feature
       return f"\n<Review: {self.text} \n Rating: {self.rating} \n Written By: {self.reviewer.prefix} {self.reviewer.firstname} {self.reviewer.lastname}>\n"