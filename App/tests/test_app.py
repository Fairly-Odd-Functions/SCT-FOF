import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import Staff, Student, Review
from App.controllers import (
    create_staff,
    get_all_staffs_json,
    # login,
    get_staff,
    # get_staff_by_staffname,
    update_staff,
    #add student to system
    add_student,
    search_student_by_student_id,
    add_review,
    get_student_reviews,
    get_student_reviews_json,
    append_review
)

LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class staffUnitTests(unittest.TestCase):

    def test_new_staff(self):
        staff = Staff("Mr.", "Johnny", "Applesauce", "johnny.applesauce@mail.com", "Y", "johnnypass", "0")
        assert staff.firstname == "Johnny"

    # pure function no side effects or integrations called
    def test_get_json(self):
        staff = Staff("Mr.", "Johnny", "Applesauce", "johnny.applesauce@mail.com", "Y", "johnnypass", "0")
        staff_json = staff.get_json()
        self.assertDictEqual(staff_json, {"id": None,
                                          "prefix": "Mr.",
                                          "firstname": "Johnny",
                                          "lastname": "Applesauce",
                                          "email": "johnny.applesauce@mail.com",
                                          "is_admin": "Y",
                                          "created_by": None})

    def test_hashed_password(self):
        password = "johnnypass"
        hashed = generate_password_hash(password, method='sha256')
        staff = Staff("Mr.", "Johnny", "Applesauce", "johnny.applesauce@mail.com", "Y", password, "0")
        assert staff.password != password

    def test_check_password(self):
        password = "johnnypass"
        staff = Staff("Mr.", "Johnny", "Applesauce", "johnny.applesauce@mail.com", "Y", password, "0")
        assert staff.check_password(password)

class StudentUnitTests(unittest.TestCase):
    def test_new_student(self):
        student = Student("815678954", "Bib", "Bibbler", "bibble@email")
        assert student.student_id == "815678954"
        assert student.firstname == "Bib"
        assert student.lastname == "Bibbler"
        assert student.email == "bibble@email"
    
    
    def test_get_json(self):
        student = Student("815678954", "Bib", "Bibbler", "bibble@email")
        studentReview = add_review(815678954, "Bob likes math", 1234567890)
        student_json = student.get_json()
        #reviews = get_student_reviews(815678954)
        self.assertDictEqual(student_json, {"student_id":"815678954", "firstname":"Bib", "lastname":"Bibbler", "email":"bibble@email", "reviews": [] } )

class ReviewUnitTests(unittest.TestCase):
    def test_new_review(self):
        review = Review("Good Student", 815678954, 123456789)
        assert review.student_id == 815678954
        assert review.text == "Good Student"
    
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

# def test_authenticate():
#     staff = create_staff("bob", "bobpass")
#     assert login("bob", "bobpass") != None

class staffsIntegrationTests(unittest.TestCase):

    def test_create_staff(self):
        johnny = create_staff("Mr.", "Johnny", "Applesauce", "johnny.applesauce@mail.com", True, "johnnypass", 0)
        rick = create_staff("Mr.", "Rick", "Rickson", "rick.rickson@mail.com", True, "rickpass", 1)
        assert johnny.firstname == "Johnny"
        assert rick.firstname == "Rick"

    def test_get_all_staffs_json(self):
        staffs_json = get_all_staffs_json()
        self.assertListEqual([{"id": 1,
                               "prefix": "Mr.",
                               "firstname": "Johnny",
                               "lastname": "Applesauce",
                               "email": "johnny.applesauce@mail.com",
                               "is_admin": True,
                               "created_by": None},

                              {"id": 2,
                               "prefix": "Mr.",
                               "firstname": "Rick",
                               "lastname": "Rickson",
                               "email": "rick.rickson@mail.com",
                               "is_admin": True,
                               "created_by": "Mr. Johnny Applesauce (johnny.applesauce@mail.com)"}], staffs_json)

    # Tests data changes in the database
    def test_update_staff(self):
        update_staff(1, "Ronnie")
        staff = get_staff(1)
        assert staff.firstname == "Ronnie"

class studentIntegrationTests(unittest.TestCase):
    def test_create_student(self):
        Heinz = add_student( 5678987654, "Heinz", "Doofenshmirtz", "DoofenshmirtzEvilEncorporated@email")
        Perry = add_student( 1234567890, "Perry", "The Platypus", "HeisPerryPerryThePlatypus@email")
        assert Heinz.student_id == 5678987654
        assert Perry.student_id == 1234567890

    def test_search_student(self):
        student = search_student_by_student_id(1234567890)
        assert student.student_id == 1234567890
        assert student.firstname == "Perry"
        assert student.lastname == "The Platypus"
    
    def test_student_review(self):
        Heinz = add_student( 5678987654, "Heinz", "Doofenshmirtz", "DoofenshmirtzEvilEncorporated@email")
        Perry = add_student( 1234567890, "Perry", "The Platypus", "HeisPerryPerryThePlatypus@email")
        review = add_review(5678987654, "Thinks he is evil", 1234567890)
        assert review.student_id == 5678987654
        assert review.text == "Thinks he is evil"
        assert review.reviewer_id == 1234567890

    def test_view_student_reviews(self):
        staff = create_staff("Mr.", "Henry", "Harvard", "henry.harvard@mail.com", True, "harvardpass", 0)
        Heinz = add_student( 567898764, "Heinz", "Doofenshmirtz", "EvilEncorporated@email")
        append_review(567898764, "Good at Science", staff.id)
        dolly = create_staff("Ms.", "Dolly", "Flynn", "dolly.flynn@mail.com", True, "dollypass", 0)
        append_review(567898764, "Talks alot about his flashbacks", dolly.id)
        review_json = get_student_reviews_json(567898764)
        print(review_json)
        self.assertListEqual([{ "student_id": 567898764, 
                                "text": "Good at Science", 
                                "reviewer": "Mr. Henry Harvard"}, 
                                
                                {"student_id" : 567898764, 
                                "text" : "Talks alot about his flashbacks", 
                                "reviewer" : "Ms. Dolly Flynn"}], review_json)
    
class reviewIntegrationTests(unittest.TestCase):
    def test_get_json(self):
        staff = create_staff("Mr.", "Bill", "Applesauce", "bill.applesauce@mail.com", True , "billpass", None)
        review = add_review(815678954,"Eats during class, very disruptive", staff.id)
        review_json = review.get_json()
        self.assertDictEqual(review_json, {"student_id": 815678954, "text":"Eats during class, very disruptive", "reviewer": "Mr. Bill Applesauce"})

