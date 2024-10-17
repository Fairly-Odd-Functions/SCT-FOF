import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.views.auth import login
from App.models import Staff, Student, Review
from App.controllers import (
    create_staff,
    add_student,
    add_review,
    get_student_json,
    get_student_reviews_json,
    get_staff,
    get_student,
    login
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

    # UNIT TEST - #1 ***
    def test_unit_01_new_student(self):
        student = Student(816000010, "Zuzu", "Pembleton", "zuzu.pembleton@mail.com")
        # Testing multiple attributes within in test function isn't needed nor a good pratice
        # Because if this test happens to fails, we don't know which attribute caused the failure
        # So checking for one attribute would be enough - JayJay
        assert student.student_id == 816000010
        assert student.firstname == "Zuzu"
        assert student.lastname == "Pembleton"
        assert student.email == "zuzu.pembleton@mail.com"
        # Or just this
        assert student is not None
    
    # UNIT TEST - #2
    def test_unit_02_new_student_json(self):
        student = Student(816000020, "Finnley", "Fothergill", "finnley.fothergill@mail.com")
        student_json = student.get_json()
        self.assertDictEqual({"student_id": 816000020,
                              "firstname": "Finnley",
                              "lastname": "Fothergill",
                              "email": "finnley.fothergill@mail.com",
                              "reviews": []}, student_json)

class StaffUnitTests(unittest.TestCase):
        # UNIT TEST - #3 ***
        # Same issue as the new student test but EVEN WORSE
        # Here we're testing a new staff but creating two types of staffs in one in the same test
        # Make separate tests for a regalur staff and admin staff, and check one thing about it.
        def test_unit_03_new_staff(self): 
            #ENSURUNG A STAFF WITH ADMIN STATUS CAN BE CREATED
            
            admin = Staff("Prof.", "Amelia", "Wilson", "amelia.wilson@mail.com", True, "amelia123", None)
            assert admin.prefix == "Prof."
            assert admin.firstname == "Amelia"
            assert admin.lastname == "Wilson"
            assert admin.email == "amelia.wilson@mail.com"
            assert admin.is_admin
            assert admin.created_by_id is None

            #ENSURING A STAFF WITHOUT ADMIN STATUS CAN BE CREATED
            staff = Staff("Mr.", "James", "Taylor", "james.taylor@mail.com", False, "jamestay", admin.id)
            assert staff.prefix == "Mr."
            assert staff.firstname == "James"
            assert staff.lastname == "Taylor"
            assert staff.email == "james.taylor@mail.com"
            assert not staff.is_admin
            #assert staff.password == generate_password_hash("jamestay")
            assert staff.created_by_id == admin.id

            assert staff is not None

        # UNIT TEST - #4
        def test_unit_04_new_staff_json(self):
            admin = Staff("Ms.", "Isabella", "Anderson", "isabella.anderson@mail.com", True, "isa_bella", None)
            staff_json = admin.get_json()
            self.assertDictEqual({"id": admin.id,
                                  "prefix": "Ms.",
                                  "firstname": "Isabella",
                                  "lastname": "Anderson",
                                  "email": "isabella.anderson@mail.com",
                                  "is_admin": True,
                                  "created_by": None}, staff_json)

        # UNIT TEST - #5
        def test_unit_05_set_password(self):
            password = "lucaspass"
            hashed_password = generate_password_hash(password)
            staff = Staff("Prof.", "Lucas", "Garcia", "lucas.garcia@mail.com", True, "lucaspass", None)
            assert staff.password != password

        # UNIT TEST - #6
        def test_unit_06_check_password(self):
            password = "henrypass"
            staff = Staff("Mr.", "Henry", "White", "henry.white@mail.com", True, password, None)
            assert staff.check_password(password)
            

class ReviewUnitTests(unittest.TestCase):
    # Isn't this an integration test? Also same problem as testing multiple attributes in one test - JayJay
    # UNIT TEST - #7 ***
    def test_unit_07_new_review(self):
        admin = Staff("Prof.", "Zoe", "Nelson", "zoe.nelson@mail.com", True, "zoenel123", None)
        student = Student(816000030, "Ethan", "Scott", "ethan.scott@mail.com")
        review = Review("Excellent effort!", 5, 816000030, admin.id)
        assert review.student_id == 816000030
        assert review.text == "Excellent effort!"
        assert review.rating == 5

        assert review is not None
    

'''
    Integration Tests
'''
class staffsIntegrationTests(unittest.TestCase):

    # INTEGRATION TEST - #1: TESTS THE AUTHENTICATION OF STAFF
    def test_integration_01_authenticate_staff_valid(self):
        new_staff = create_staff("Mr.", "Johnny", "Applesauce", "johnny.applesauce@mail.com", True, "johnnypass", None)
        response = login("johnny.applesauce@mail.com", "johnnypass")
        assert response is not None

    # INTEGRATION TEST - #2: TESTS THE AUTHENTICATION FAILURE OF STAFF
    def test_integration_02_authenticate_staff_invalid(self):
        new_staff = create_staff("Dr.", "Emily", "Chen", "emily.chen@mail.com", True, "emilypass", None)
        response = login("emily.chen@mail.com", "wrongpassword")
        assert response is None

    # INTEGRATION TEST - #3: TESTS THE CREATION OF STAFF BY AN ADMIN ***
    # Testing too many attributes - JayJay
    def test_integration_03_create_staff(self):
        new_admin = create_staff("Ms.", "David", "Lee", "david.lee@mail.com", True, "davidpass", None)
        new_staff = create_staff("Prof.", "Sophia", "Patel", "sophia.patel@mail.com", False, "sophiypass", new_admin.id)

        self.assertIsNotNone(new_staff)
        self.assertEqual(new_staff.prefix, 'Prof.')
        self.assertEqual(new_staff.firstname, 'Sophia')
        self.assertEqual(new_staff.lastname, 'Patel')
        self.assertEqual(new_staff.email, 'sophia.patel@mail.com')
        self.assertTrue(check_password_hash(new_staff.password, 'sophiypass'))
        self.assertFalse(new_staff.is_admin)

        fetched_staff = get_staff(new_staff.id)
        self.assertIsNotNone(fetched_staff)     #should I check for equality in all fields?
        
    # INTEGRATION TEST - #4: TESTS THE CREATION/ADDING OF A NEW STUDENT ***
    def test_integration_04_add_student(self):
        new_admin = create_staff("Prof.", "Jackson", "Wang", "jackson.wang@mail.com", True, "jacksonpass", None)
        new_staff = create_staff("Mr.", "Liam", "Kim", "liam.kim@mail.com", False, "liampass", new_admin.id)

        # ********** There is no real testable difference between these two?
        # Both staff are staff regardless, also had the logic problem, if one fails we won't know which caused it

        #ENSURING AN ADMIN CAN CREATE A STUDENT  **********
        new_student2 = add_student("816000001","Ava", "Brown", "ava.brown@mail.com")
        self.assertEqual(new_student2.firstname, "Ava")
        self.assertEqual(new_student2.lastname, "Brown")
        self.assertEqual(new_student2.email, "ava.brown@mail.com")

        #ENSURING A STAFF CAN CREATE A STUDENT **********
        new_student2 = add_student("816000002","Rick", "Rickson", "rick.rickson@mail.com")
        self.assertEqual(new_student2.firstname, "Rick")
        self.assertEqual(new_student2.lastname, "Rickson")
        self.assertEqual(new_student2.email, "rick.rickson@mail.com")

        fetched_student1 = get_student(816000001)
        fetched_student2 = get_student(816000002)

        self.assertIsNotNone(fetched_student1)
        self.assertIsNotNone(fetched_student2)

    # INTEGRATION TEST - #5: TESTS THE SEARCH OF AN EXISTING STUDENT
    def test_integration_05_get_student_json(self):
        new_admin = create_staff("Prof.", "Julian", "Lee", "julian.lee@mail.com", True, "julianpass", None)
        new_student = add_student("816000003","Ethan", "Hall", "ethan.hall@mail.com")

        response = get_student_json(816000003)
        self.assertDictEqual({"student_id": 816000003,
                               "firstname": "Ethan", 
                               "lastname": "Hall", 
                               "email": "ethan.hall@mail.com",
                               "reviews": []}, response)
        
    # INTEGRATION TEST - #6: TESTS THE ADDING OF REVIEW FOR A STUDENT ***
    def test_integration_06_add_student_reviews(self):
        # Same as above
        new_admin = create_staff("Ms.", "Sophia", "Taylor", "sophia.taylor@mail.com", True, "sophiapass", None)
        new_staff = create_staff("Mr.", "Oliver", "Martin", "oliver.martin@mail.com", False, "oliverpass", new_admin.id)
        new_student = add_student("816000004","Mia", "Davis", "mia.davis@mail.com")

        #ENSURING AN ADMIN ADD REVIEW TO A STUDENT ***
        response1 = add_review("816000004", "Great student", 5, new_admin.id)
        assert(len(new_admin.reviews) == 1) # Huh? What if this same admin made multiple reviews towards other students?
        self.assertEqual(response1.student_id, 816000004)
        self.assertEqual(response1.text, "Great student")
        self.assertEqual(response1.rating, 5)
        self.assertEqual(response1.reviewer_id, new_admin.id)

        #ENSURING A STAFF CAN ADD REVIEW TO A STUDENT ***
        response2 = add_review("816000004", "Bad student", 1, new_staff.id)
        assert(len(new_staff.reviews) == 1) 
        self.assertEqual(response2.student_id, 816000004)
        self.assertEqual(response2.text, "Bad student")
        self.assertEqual(response2.rating, 1)
        self.assertEqual(response2.reviewer_id, new_staff.id)

    # INTEGRATION TEST - #7: TESTS THE RETRIEVAL OF ALL REVIEWS FOR A STUDENT
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

    # INTEGRATION TEST - #8: TESTS THE RETRIEVAL OF ALL REVIEWS FOR A STAFF
    # Don't really need this but I don't really need a problem with it tbh
    def test_integration_08_get_staff_reviews_json(self):
        new_admin = create_staff("Dr.", "Eve", "Hall", "eve.hall@mail.com", True, "evepass", None)
        new_student1 = add_student("816000006", "Juliana", "Brown", "juliana.brown@mail.com")
        new_student2 = add_student("816000007", "Llyod", "Green", "llyod.green@mail.com")

        add_review("816000006", "Great student", 5, new_admin.id)
        add_review("816000007", "Bad student", 1, new_admin.id)

        staff = get_staff(new_admin.id)
        reviews = staff.reviews
        reviews = [review.get_json() for review in staff.reviews]
        self.assertListEqual([{"student_id": 816000006,
                               "text": "Great student", 
                               "rating": 5, 
                               "reviewer": "Dr. Eve Hall"},
                               
                               {"student_id": 816000007,
                                "text": "Bad student", 
                                "rating": 1, 
                                "reviewer": "Dr. Eve Hall"}], reviews)