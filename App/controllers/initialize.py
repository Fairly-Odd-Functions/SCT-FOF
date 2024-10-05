from .staff import create_staff
from App.database import db

def initialize():
    db.drop_all()
    db.create_all()
    create_staff('Mr.', 'Bob', 'Bobberson', 'bob.bobberson@mail.com', True, 'bobpass', 0)
    create_staff('Mr.', 'Bobby', 'Butterbread', 'bobby.butterbread@mail.com', False, 'bobbypass', 0)

    from App.main import parse_reviews, parse_students
    
    parse_reviews()
    parse_students("students.csv")
