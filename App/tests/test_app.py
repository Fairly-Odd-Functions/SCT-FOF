import os, tempfile, pytest, logging, unittest

from App.main import create_app
from App.database import db, create_db
from App.views.auth import login
from App.models import Staff, Student
from App.controllers import (
    create_staff,
    add_student,
    add_review,
    get_student_json,
    get_student_reviews_json,
)

LOGGER = logging.getLogger(__name__)

#  fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()

'''
   Unit Tests
'''
class StudentUnitTests(unittest.TestCase):

    # UNIT TEST - #1: STUDENT
    def test_unit_01_new_student(self):
        student = Student(816000010, "Zuzu", "Pembleton", "zuzu.pembleton@mail.com")
        assert student.email == "zuzu.pembleton@mail.com"

    # UNIT TEST - #2: STUDENT JSON
    def test_unit_02_new_student_json(self):
        student = Student(816000020, "Finnley", "Fothergill", "finnley.fothergill@mail.com")
        student_json = student.get_json()
        self.assertDictEqual({"student_id": 816000020,
                              "firstname": "Finnley",
                              "lastname": "Fothergill",
                              "email": "finnley.fothergill@mail.com",
                              "reviews": []}, student_json)

class StaffUnitTests(unittest.TestCase):

    # UNIT TEST - #3: REGULAR STAFF
    def test_unit_03_new_regular_staff(self): 
        staff = Staff("Mr.", "James", "Taylor", "james.taylor@mail.com", False, "jamespass", None)
        assert not staff.is_admin

    # UNIT TEST - #4: ADMIN STAFF
    def test_unit_04_new_admin_staff(self):
        staff = Staff("Prof.", "Amelia", "Wilson", "amelia.wilson@mail.com", True, "ameliapass", None)
        assert staff.is_admin

    # UNIT TEST - #5: STAFF JSON
    def test_unit_05_new_staff_json(self):
        new_staff = Staff("Ms.", "Isabella", "Anderson", "isabella.anderson@mail.com", True, "isabellapass", None)
        staff_json = new_staff.get_json()
        self.assertDictEqual({"id": new_staff.id,
                                "prefix": "Ms.",
                                "firstname": "Isabella",
                                "lastname": "Anderson",
                                "email": "isabella.anderson@mail.com",
                                "is_admin": True,
                                "created_by": None}, staff_json)

    # UNIT TEST - #6: SET PASSWORD
    def test_unit_06_set_password(self):
        password = "lucaspass"
        staff = Staff("Prof.", "Lucas", "Garcia", "lucas.garcia@mail.com", True, password, None)
        assert staff.password != password

    # UNIT TEST - #7: CHECK PASSWORD
    def test_unit_07_check_password(self):
        password = "henrypass"
        staff = Staff("Mr.", "Henry", "White", "henry.white@mail.com", True, password, None)
        assert staff.check_password(password)

'''
    Integration Tests
'''
class StaffIntegrationTests(unittest.TestCase):

    # INTEGRATION TEST - #1: TESTS THE AUTHENTICATION SUCCESS
    def test_integration_01_authenticate_staff_valid(self):
        new_staff = create_staff("Mr.", "Johnny", "Applesauce", "johnny.applesauce@mail.com", True, "johnnypass", None)
        response = login(new_staff.email, "johnnypass")
        assert response is not None

    # INTEGRATION TEST - #2: TESTS AUTHENTICATION FAILURE
    def test_integration_02_authenticate_staff_invalid(self):
        new_staff = create_staff("Dr.", "Emily", "Chen", "emily.chen@mail.com", True, "emilypass", None)
        response = login(new_staff.email, "notemilypass")
        assert response is None

    # INTEGRATION TEST - #3: CREATE A NEW STAFF
    def test_integration_03_create_staff(self):
        new_admin = create_staff("Ms.", "David", "Lee", "david.lee@mail.com", True, "davidpass", None)
        new_staff = create_staff("Prof.", "Sophia", "Patel", "sophia.patel@mail.com", False, "sophiapass", new_admin.id)
        assert new_staff.email == "sophia.patel@mail.com"
        
    # INTEGRATION TEST - #4: ADD A NEW STUDENT
    def test_integration_04_add_student(self):
        new_student = add_student("816000001","Ava", "Brown", "ava.brown@mail.com")
        assert new_student.email == "ava.brown@mail.com"

    # INTEGRATION TEST - #5: SEARCHING AN EXISTING STUDENT
    def test_integration_05_get_student_json(self):
        new_student = add_student("816000003","Ethan", "Hall", "ethan.hall@mail.com")
        response = get_student_json(new_student.student_id)
        self.assertDictEqual({"student_id": 816000003,
                               "firstname": "Ethan", 
                               "lastname": "Hall", 
                               "email": "ethan.hall@mail.com",
                               "reviews": []}, response)

    # INTEGRATION TEST - #6: REVIEWING A STUDENT
    def test_integration_06_add_student_reviews(self):
        new_admin = create_staff("Ms.", "Sophia", "Taylor", "sophia.taylor@mail.com", True, "sophiapass", None)
        new_staff = create_staff("Mr.", "Oliver", "Martin", "oliver.martin@mail.com", False, "oliverpass", new_admin.id)
        new_student = add_student("816000004","Mia", "Davis", "mia.davis@mail.com")
        new_review = add_review(new_student.student_id, "Very Good Student", 5, new_staff.id)
        assert new_review.text == "Very Good Student"

    # INTEGRATION TEST - #7: RETRIEVING ALL STUDENT REVIEWS
    def test_integration_07_get_student_reviews_json(self):
        new_admin = create_staff("Dr.", "Evelyn", "Hall", "evelyn.hall@mail.com", True, "evelynpass", None)
        new_staff = create_staff("Ms.", "Ava", "Lee", "ava.lee@mail.com", False, "avapass", new_admin.id)
        new_student = add_student("816000005", "Julian", "Brown", "julian.brown@mail.com")

        add_review(new_student.student_id, "Very Good Student", 5, new_admin.id)
        add_review(new_student.student_id, "Very Bad Student", 1, new_staff.id)

        reviews = get_student_reviews_json(new_student.student_id)
        self.assertListEqual([{"student_id": 816000005,
                               "text": "Very Good Student", 
                               "rating": 5, 
                               "reviewer": "Dr. Evelyn Hall"},
                              
                               {"student_id": 816000005,
                               "text": "Very Bad Student", 
                               "rating": 1, 
                               "reviewer": "Ms. Ava Lee"}], reviews)
