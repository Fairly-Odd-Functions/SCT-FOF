import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db

from App.controllers import (
    create_staff,
    get_staff,
    add_student,
    get_student,
    add_review,
    get_student_reviews_json
)

from App.models.staff import Staff
from App.views.auth import login

LOGGER = logging.getLogger(__name__)


'''
   Unit Tests
'''

#[LEFT EMPTY FOR EASE OF MERGING LATER]


'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()


class staffsIntegrationTests(unittest.TestCase):

    #INTEGRATION TEST-#1
    def test_authenticate_staff_valid(self):
        jhonny = create_staff("Mr.", "Johnny", "Applesauce", "johnny.applesauce@mail.com", False, "johnnypass", 1)
        response = login("johnny.applesauce@mail.com", "johnnypass")
        assert response is not None

    #INTEGRATION TEST-#2
    def test_authenticate_staff_invalid(self):
        response = login("johnny.applesauce@mail.com", "wrongpassword")
        assert response is None

    #INTEGRATION TEST-#3 [TO DEBUGG]
    # def test_create_staff(self):

    #     create_staff('Mr.', 'Bob', 'Bobberson', 'bob.bobberson@mail.com', True, 'bobpass', 0)

    #     newstaff = create_staff("Mr.", "Susan", "Smith", "susan.smith@mail.com", True, "susanpass", 0)
    #     self.assertEqual(newstaff.firstname, "Susan")
    #     self.assertEqual(newstaff.lastname, "Smith")
    #     self.assertEqual(newstaff.email, "susan.smith@mail.com")
    #     self.assertTrue(newstaff.is_admin)
    #     self.assertTrue(check_password_hash(newstaff.password, "susanpass"))
    #     self.assertEqual(newstaff.created_by_id, 0)
        
    #INTEGRATION TEST-#4
    def test_add_student(self):
        newstudent = add_student("816012345", "Rick", "Rickson", "rick.rickson@mail.com")
        self.assertEqual(newstudent.firstname, "Rick")
        self.assertEqual(newstudent.lastname, "Rickson")
        self.assertEqual(newstudent.email, "rick.rickson@mail.com")

    #INTEGRATION TEST-#5
    def test_view_staff_reviews(self):
        staff = get_staff(1)
        student = get_student(816012345)

        add_review(816012345, "Great student", 5, 1)
        assert(len(staff.reviews) == 1)
        
        review = staff.reviews[0]
        self.assertEqual(review.student_id, 816012345)
        self.assertEqual(review.text, "Great student")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.reviewer_id, 1)

    #INTEGRATION TEST-#6
    def test_search_student(self):
        student = get_student(816012345)
        self.assertEqual(student.firstname, "Rick")
        self.assertEqual(student.lastname, "Rickson")
        self.assertEqual(student.email, "rick.rickson@mail.com")

    # #INTEGRATION TEST-#7 [TO DEBUGG]
    # def test_get_student_reviews_json(self):
    #     reviews = get_student_reviews_json(816012345)

    #     self.assertListEqual([{"student_id": 816012345, 
    #                            "text": "Great student", 
    #                            "rating": 5, 
    #                            "reviewer_id": 1}], reviews)
    

    # - - - - - [SIR'S EXAMPLES BELOW]  - - - - - - -
    # def test_get_all_staffs_json(self):
    #     staffs_json = get_all_staffs_json()
    #     self.assertListEqual([{"id": 1,
    #                            "prefix": "Mr.",
    #                            "firstname": "Susan",
    #                            "lastname": "Smith",
    #                            "email": "susan.smith@mail.com",
    #                            "is_admin": True,
    #                            "created_by": None},

    #                           {"id": 2,
    #                            "prefix": "Mr.",
    #                            "firstname": "Rick",
    #                            "lastname": "Rickson",
    #                            "email": "rick.rickson@mail.com",
    #                            "is_admin": True,
    #                            "created_by": "Mr. Johnny Applesauce (johnny.applesauce@mail.com)"}], staffs_json)

    # Tests data changes in the database
    # def test_update_staff(self):
    #     update_staff(1, "Ronnie")
    #     staff = get_staff(1)
    #     assert staff.firstname == "Ronnie"