from App.database import db
from App.models import Staff

# Create A Staff (Regular & Admin)
def create_staff(prefix, firstname, lastname, email, is_admin, password, created_by_id):
    try:
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
    except Exception as e:
        print(f"Error While Creating Staff: {e}")
        db.session.rollback()
        return None

# Get Staff
def get_staff(id):
    return Staff.query.get(id)

# Get Staff Via Email - Unique Identification
def get_staff_by_email(email):
    return Staff.query.filter_by(email=email).first()