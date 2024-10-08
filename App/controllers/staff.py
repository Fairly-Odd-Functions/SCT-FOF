from App.controllers.student import get_student, get_student_record, check_student_email
from App.models import Student, Review
from App.models import Staff
from App.database import db

def create_staff(prefix, firstname, lastname, email, is_admin, password, created_by_id):
    created_by = get_staff(created_by_id)

    existing_staff = get_staff_by_email(email)
    if existing_staff is not None:
        return None

    if created_by and created_by.is_admin:
        newstaff = Staff(prefix=prefix,
                        firstname=firstname,
                        lastname=lastname,
                        email=email,
                        is_admin=is_admin,
                        created_by_id=created_by_id,
                        password=password)
        db.session.add(newstaff)
        db.session.commit()
        return newstaff

    elif created_by and not created_by.is_admin:
        return None

    else:
        newstaff = Staff(prefix=prefix, 
                        email=email, 
                        firstname=firstname, 
                        lastname=lastname, 
                        is_admin=is_admin,
                        created_by_id=None,
                        password=password)
        db.session.add(newstaff)
        db.session.commit()
        return newstaff

def get_staff(id):
    return Staff.query.get(id)

def get_staff_by_email(email):
    return Staff.query.filter_by(email=email).first()

def get_all_staffs():
    return Staff.query.all()

def get_all_staffs_json():
    staffs = Staff.query.all()
    if not staffs:
        return []
    staffs = [staff.get_json() for staff in staffs]
    return staffs

def update_staff(id, firstname):
    staff = get_staff(id)
    if staff:
        staff.firstname = firstname
        db.session.add(staff)
        return db.session.commit()
    return None

def add_student (student_id, firstname, lastname, email):
    existing_student = get_student(student_id)
    get_student_email = check_student_email(email)

    if existing_student or get_student_email is not None:
        return None
    else:
        new_student = Student(student_id, firstname=firstname, lastname=lastname, email=email)
        db.session.add(new_student)
        db.session.commit()
        return new_student

def search_student_by_student_id(student_id):
    return get_student_record(student_id)

def add_review(student_id, text, rating, reviewer_id):
    student_review = Review(student_id=student_id, text=text, rating=rating, reviewer_id=reviewer_id)
    db.session.add(student_review)
    db.session.commit()
    return student_review