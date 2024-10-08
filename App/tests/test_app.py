import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import Staff
from App.controllers import (
    create_staff,
    login
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

def test_authenticate():
    staff = create_staff("Mr.", "James", "Pearsauce", "james.pearsauce@mail.com", True, "jamespass", 0)
    assert login("james.pearsauce@mail.com", "jamespass") != None
    
class staffsIntegrationTests(unittest.TestCase):

    def test_create_staff(self):
        johnny = create_staff("Mr.", "Johnny", "Applesauce", "johnny.applesauce@mail.com", True, "johnnypass", 0)
        rick = create_staff("Mr.", "Rick", "Rickson", "rick.rickson@mail.com", True, "rickpass", 1)
        assert johnny.firstname == "Johnny"
        assert rick.firstname == "Rick"