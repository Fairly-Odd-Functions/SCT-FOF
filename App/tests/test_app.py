import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.views.auth import login
from App.models import Staff, Student, Review
from App.controllers import (
    create_staff,
    add_student,
    get_student_record_json,

    add_review,
    get_student_reviews_json,
    add_student,
    add_review,
    get_student_reviews_json
)

LOGGER = logging.getLogger(__name__)

# This fixture creates an empty database for the test and deletes it after the test
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
class staffsIntegrationTests(unittest.TestCase):

    #INTEGRATION TEST-#1:   THIS TESTS THE AUTHENTICATION OF STAFF
    def test_integration_01_authenticate_staff_valid(self):
        new_staff = create_staff("Mr.", "Johnny", "Applesauce", "johnny.applesauce@mail.com", True, "johnnypass", None)
        response = login("johnny.applesauce@mail.com", "johnnypass")
        assert response is not None

    #INTEGRATION TEST-#2    THIS TESTS THE AUTHENTICATION FAILURE OF STAFF
    def test_integration_02_authenticate_staff_invalid(self):
        new_staff = create_staff("Dr.", "Emily", "Chen", "emily.chen@mail.com", True, "emilypass", None)
        response = login("emily.chen@mail.com", "wrongpassword")
        assert response is None

    #INTEGRATION TEST-#3    THIS TESTS THE CREATION OF STAFF BY AN ADMIN
    def test_integration_03_create_staff(self):
        new_admin = create_staff("Ms.", "David", "Lee", "david.lee@mail.com", True, "davidpass", None)
        newstaff = create_staff("Prof.", "Sophia", "Patel", "sophia.patel@mail.com", False, "sophiypass", new_admin.id)

        self.assertIsNotNone(newstaff)
        self.assertEqual(newstaff.prefix, 'Prof.')
        self.assertEqual(newstaff.firstname, 'Sophia')
        self.assertEqual(newstaff.lastname, 'Patel')
        self.assertEqual(newstaff.email, 'sophia.patel@mail.com')
        self.assertTrue(check_password_hash(newstaff.password, 'sophiypass'))
        self.assertFalse(newstaff.is_admin)
        
    #INTEGRATION TEST-#4    THIS TEST TESTS THE CREATION/ADDING OF A NEW STUDENT
    def test_integration_04_add_student(self):
        new_admin = create_staff("Prof.", "Jackson", "Wang", "jackson.wang@mail.com", True, "jacksonpass", None)
        new_staff = create_staff("Mr.", "Liam", "Kim", "liam.kim@mail.com", False, "liampass", new_admin.id)

        #ENSURING AN ADMIN CAN CREATE A STUDENT
        new_student2 = add_student("816000001","Ava", "Brown", "ava.brown@mail.com")
        self.assertEqual(new_student2.firstname, "Ava")
        self.assertEqual(new_student2.lastname, "Brown")
        self.assertEqual(new_student2.email, "ava.brown@mail.com")

        #ENSURING A STAFF CAN CREATE A STUDENT
        new_student2 = add_student("816000002","Rick", "Rickson", "rick.rickson@mail.com")
        self.assertEqual(new_student2.firstname, "Rick")
        self.assertEqual(new_student2.lastname, "Rickson")
        self.assertEqual(new_student2.email, "rick.rickson@mail.com")


    #INTEGRATION TEST-#5    THIS TEST TESTS THE SEARCH OF AN ADDED STUDENT
    def test_integration_05_search_student_json(self):
        new_admin = create_staff("Prof.", "Julian", "Lee", "julian.lee@mail.com", True, "julianpass", None)
        new_student = add_student("816000003","Ethan", "Hall", "ethan.hall@mail.com")

        response = get_student_record_json(816000003)
        self.assertDictEqual({"student_id": 816000003,
                               "firstname": "Ethan", 
                               "lastname": "Hall", 
                               "email": "ethan.hall@mail.com",
                               "reviews": []}, response)
        
    #INTEGRATION TEST-#6    THIS TEST TESTS THE ADDING OF REVIEW FOR A STUDENT
    def test_integration_06_add_student_reviews(self):
        new_admin = create_staff("Ms.", "Sophia", "Taylor", "sophia.taylor@mail.com", True, "sophiapass", None)
        new_staff = create_staff("Mr.", "Oliver", "Martin", "oliver.martin@mail.com", False, "oliverpass", new_admin.id)
        new_student = add_student("816000004","Mia", "Davis", "mia.davis@mail.com")

        #ENSURING AN ADMIN ADD REVIEW TO A STUDENT
        response1 = add_review("816000004", "Great student", 5, new_admin.id)
        assert(len(new_admin.reviews) == 1)
        self.assertEqual(response1.student_id, 816000004)
        self.assertEqual(response1.text, "Great student")
        self.assertEqual(response1.rating, 5)
        self.assertEqual(response1.reviewer_id, new_admin.id)

        #ENSURING A STAFF CAN ADD REVIEW TO A STUDENT
        response2 = add_review("816000004", "Bad student", 1, new_staff.id)
        assert(len(new_staff.reviews) == 1)
        self.assertEqual(response2.student_id, 816000004)
        self.assertEqual(response2.text, "Bad student")
        self.assertEqual(response2.rating, 1)
        self.assertEqual(response2.reviewer_id, new_staff.id)

    #INTEGRATION TEST-#7    THIS TEST TESTS THE RETRIEVAL OF ALL REVIEWS FOR A STUDENT
    def test_integration_07_get_student_reviews_json(self):
        new_admin = create_staff("Dr.", "Evelyn", "Hall", "evelyn.hall@mail.com", True, "evelynpass", None)
        new_staff = create_staff("Ms.", "Ava", "Lee", "ava.lee@mail.com", False, "avapass", new_admin.id)
        new_student = add_student("816000005", "Julian", "Brown", "julian.brown@mail.com")

        add_review("816000005", "Great student", 5, new_admin.id)
        add_review("816000005", "Bad student", 1, new_staff.id)

        reviews = get_student_reviews_json(816000005)
        self.assertListEqual([{"student_id": 816000005,
                               "text": "Great student", 
                               "rating": 5, 
                               "reviewer": "Dr. Evelyn Hall"},
                               
                               {"student_id": 816000005,
                               "text": "Bad student", 
                               "rating": 1, 
                               "reviewer": "Ms. Ava Lee"}], reviews)   


# - - - - - - - - - - [THIS TEST BELOW IS ALREADY COVERED @TEST_07] - - - - - - - - - - - - - - - -

# class reviewIntegrationTests(unittest.TestCase):
#     def test_get_json(self):
#         staff = create_staff("Mr.", "Bill", "Applesauce", "bill.applesauce@mail.com", True , "billpass", None)
#         review = add_review(815678954,"Eats during class, very disruptive", 2,  staff.id)
#         review_json = review.get_json()
#         self.assertDictEqual(review_json, {"student_id": 815678954, "text":"Eats during class, very disruptive", "rating":2, "reviewer": "Mr. Bill Applesauce"})

#         student = get_student(816012345)

#         add_review(816012345, "Great student", 5, staff.id)
#         assert(len(staff.reviews) == 1)
        
#         review = staff.reviews[0]
#         self.assertEqual(review.student_id, 816012345)
#         self.assertEqual(review.text, "Great student")
#         self.assertEqual(review.rating, 5)
#         self.assertEqual(review.reviewer_id, 1) 


# - - - - - - - - - - - - - - [SIR'S EXAMPLES BELOW] - - - - - - - - - - - - - - - - - - - - - - -

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