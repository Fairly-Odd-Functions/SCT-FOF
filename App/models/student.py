from App.database import db

class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    email =  db.Column(db.String, nullable=False, unique=True)
    reviews = db.relationship('Review', back_populates='reviewee')

    def __init__(self, student_id, firstname, lastname, email):
        self.student_id = student_id
        self.firstname = firstname
        self.lastname = lastname
        self.email = email

    def get_json(self):
        return{
            'student_id': self.student_id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'reviews': [review.text for review in self.reviews],
        }

    def __repr__(self):
        return f"<Student: {self.student_id} | {self.firstname} {self.lastname} | {self.email} | {[review.text for review in self.reviews]}>"