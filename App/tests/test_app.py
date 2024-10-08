import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.views.auth import login
from App.models import Staff, Student, Review
from App.controllers import (
    create_staff,
    get_staff,
    update_staff,
    add_student,
    search_student_by_student_id,
    add_review,
    get_student_reviews,
    get_student_reviews_json,
    append_review,
    add_student,
    get_student,
    add_review,
    get_student_reviews_json
)

LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''

class StudentUnitTests(unittest.TestCase):
    def test_new_student(self):
        student = Student("815678954", "Bib", "Bibbler", "bibble@email")
        assert student.student_id == "815678954"
        assert student.firstname == "Bib"
        assert student.lastname == "Bibbler"
        assert student.email == "bibble@email"
        
    def test_get_json(self):
        student = Student("815678954", "Bib", "Bibbler", "bibble@email")
        studentReview = add_review(815678954, "Bob likes math", 3, 1234567890)
        student_json = student.get_json()
        #reviews = get_student_reviews(815678954)
        self.assertDictEqual(student_json, {"student_id":"815678954", "firstname":"Bib", "lastname":"Bibbler", "email":"bibble@email", "reviews": [] } )
        
class ReviewUnitTests(unittest.TestCase):
    def test_new_review(self):
        review = Review("Good Student", 5,  815678954, 123456789)
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


class staffsIntegrationTests(unittest.TestCase):

    #INTEGRATION TEST-#1
    def test_01_authenticate_staff_valid(self):
        newstaff = create_staff("Mr.", "Johnny", "Applesauce", "johnny.applesauce@mail.com", True, "johnnypass", 1)
        response = login("johnny.applesauce@mail.com", "johnnypass")
        assert response is not None

    #INTEGRATION TEST-#2
    def test_02_authenticate_staff_invalid(self):
        response = login("johnny.applesauce@mail.com", "wrongpassword")
        assert response is None

    #INTEGRATION TEST-#3
    def test_03_create_staff(self):
        admin_creator = get_staff(1)
        
        newstaff = create_staff('Mr', 'John', 'Doe', 'johndoe@example.com', False, 'johnpass', admin_creator.id)
        self.assertIsNotNone(newstaff)
        self.assertEqual(newstaff.prefix, 'Mr')
        self.assertEqual(newstaff.firstname, 'John')
        self.assertEqual(newstaff.lastname, 'Doe')
        self.assertEqual(newstaff.email, 'johndoe@example.com')
        self.assertTrue(check_password_hash(newstaff.password, 'johnpass'))
        self.assertFalse(newstaff.is_admin)
        
    #INTEGRATION TEST-#4
    def test_04_add_student(self):
        newstudent = add_student("816012345", "Rick", "Rickson", "rick.rickson@mail.com")
        self.assertEqual(newstudent.firstname, "Rick")
        self.assertEqual(newstudent.lastname, "Rickson")
        self.assertEqual(newstudent.email, "rick.rickson@mail.com")
      
    #INTEGRATION TEST-#5
    def test_05_search_student(self):
        student = get_student(816012345)
        self.assertEqual(student.firstname, "Rick")
        self.assertEqual(student.lastname, "Rickson")
        self.assertEqual(student.email, "rick.rickson@mail.com")

    #INTEGRATION TEST-#6
    def test_06_view_staff_reviews(self):
        staff = get_staff(1)
        assert staff.firstname == "Ronnie"
    
        # #INTEGRATION TEST-#7
    def test_07_get_student_reviews_json(self):
        reviews = get_student_reviews_json(816012345)
        self.assertListEqual([{"student_id": 816012345, 
                               "text": "Great student", 
                               "rating": 5, 
                               "reviewer": "Mr. Johnny Applesauce"}], reviews)

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
        staff = create_staff("Mr.", "Tom", "Sawyer", "tom@email.com", True, "tompass", 0)
        review = add_review(5678987654, "Thinks he is evil", 1, staff.id)
        assert review.student_id == 5678987654
        assert review.text == "Thinks he is evil"
        assert review.rating == 1
        assert review.reviewer_id == staff.id

    def test_view_student_reviews(self):
        staff = create_staff("Mr.", "Henry", "Harvard", "henry.harvard@mail.com", True, "harvardpass", 0)
        Heinz = add_student( 567898764, "Heinz", "Doofenshmirtz", "EvilEncorporated@email")
        append_review(567898764, "Good at Science", 5, staff.id)
        dolly = create_staff("Ms.", "Dolly", "Flynn", "dolly.flynn@mail.com", True, "dollypass", 0)
        append_review(567898764, "Talks alot about his flashbacks", 4, dolly.id)
        review_json = get_student_reviews_json(567898764)
        print(review_json)
        self.assertListEqual([{ "student_id": 567898764, 
                                "text": "Good at Science", 
                                "rating": 5,
                                "reviewer": "Mr. Henry Harvard"}, 
                                
                                {"student_id" : 567898764, 
                                "text" : "Talks alot about his flashbacks",
                                "rating" : 4 ,
                                "reviewer" : "Ms. Dolly Flynn"}], review_json)
    
class reviewIntegrationTests(unittest.TestCase):
    def test_get_json(self):
        staff = create_staff("Mr.", "Bill", "Applesauce", "bill.applesauce@mail.com", True , "billpass", None)
        review = add_review(815678954,"Eats during class, very disruptive", 2,  staff.id)
        review_json = review.get_json()
        self.assertDictEqual(review_json, {"student_id": 815678954, "text":"Eats during class, very disruptive", "rating":2, "reviewer": "Mr. Bill Applesauce"})

        student = get_student(816012345)

        add_review(816012345, "Great student", 5, staff.id)
        assert(len(staff.reviews) == 1)
        
        review = staff.reviews[0]
        self.assertEqual(review.student_id, 816012345)
        self.assertEqual(review.text, "Great student")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.reviewer_id, 1)

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
