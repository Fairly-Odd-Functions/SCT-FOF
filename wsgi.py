import click, pytest, sys # type: ignore
from flask import Flask # type: ignore
from flask.cli import with_appcontext, AppGroup # type: ignore

from App.database import db, get_migrate
from App.main import create_app, parse_students
from App.controllers import ( create_staff, get_all_staffs_json, get_all_staffs, initialize, add_student, search_student_by_student_id, add_review, initialize )
from App.controllers.student import ( get_all_students_json, get_all_students, get_student, get_student_reviews, get_student_reviews_json )
from App.models.staff import Staff

app = create_app()
migrate = get_migrate(app)

# This Command Creates & Initializes The Database
@app.cli.command("init", help="Creates & Initializes The Database")
def init():
    initialize()
    print('Database Intialized!')

'''
Admin Commands
'''

admin_cli = AppGroup('admin', help='Admin Object Commands') 
# eg : flask admin <command>

# EXTRA #1 - CREATE STAFF ACCOUNT
@admin_cli.command("create_staff", help="Creates A Staff Account")
@click.argument("prefix", required=False)
@click.argument("firstname", required=False)
@click.argument("lastname", required=False)
@click.argument("email", required=False)
@click.argument("is_admin_input", required=False)
@click.argument("password", required=False)
@click.argument("created_by_id", required=False)
def create_staff_command(prefix, firstname, lastname, email, is_admin_input, password, created_by_id):
    if prefix is None:
        prefix = input("Enter Staff Prefix: ")
    if firstname is None:
        firstname = input("Enter Staff First Name: ")
    if lastname is None:
        lastname = input("Enter Staff Last Name: ")
    if email is None:
        email = input("Enter Staff Email: ")
    if is_admin_input is None:
        is_admin_input = input("Is This Staff An Admin? (Y/N): ")
    is_admin = True if is_admin_input.lower() == 'y' else False
    if password is None:
        password = input("Enter Staff Default Password: ")
    if created_by_id is None:
        created_by_id = input("Enter Your Admin ID: ")

    existing_staff = Staff.query.filter_by(email=email).first()

    if existing_staff:
        print("ERROR: A Staff Already Exists With That Email.")
        return

    new_staff = create_staff(prefix, firstname, lastname, email, is_admin, password, created_by_id)
    if new_staff:
        print(f'Staff Account For {prefix + " " + firstname + " " + lastname} Created!')
    else:
        print("ERROR: Unauthorized - Admins Only.")

app.cli.add_command(admin_cli)

# EXTRA #2 - LIST ALL STAFF ACCOUNTS IN DATABASE 
@admin_cli.command("list_staff", help="Lists All Staff Account In The Database")
@click.argument("format", default="string")
def list_staff_command(format):
    if format == 'string':
        print(get_all_staffs())
    else:
        print(get_all_staffs_json())

'''
Staff Commands
'''

staff_cli = AppGroup('staff', help='Admin Object Commands') 
# eg : flask staff <command>

# REQUIREMENT #1 - ADD STUDENT
@staff_cli.command("add_student", help="Adds A Student Record")
@click.argument("student_id", required=False)
@click.argument("firstname", required=False)
@click.argument("lastname", required=False)
@click.argument("email", required=False)
def add_student_command(student_id, firstname, lastname, email):
    if student_id is None:
        student_id = input("Enter Student ID: ")
    if firstname is None:
        firstname = input("Enter Student First Name: ")
    if lastname is None:
        lastname = input("Enter Lastname Last Name: ")
    if email is None:
        email = input("Enter Student Email: ")
    new_student = add_student(student_id, firstname, lastname, email)
    if new_student:
        print(f"A Record Has Been Made For Student: {firstname + ' ' + lastname}.")
    else:
        print(f"ERROR: A Student With That ID Already Exists In The Database!")
 
# REQUIREMENT #1 EXTENSION - IMPORT CSV OF STUDENTS - For Convenience
@staff_cli.command("add_students", help="Adds Multiple Students Via CSV")
@click.argument("filepath", required=False)
def add_students_command(filepath):
    if filepath is None:
        filepath = input("Enter Filepath: ")
    parse_students(filepath)
    print(f"All Students Added From CSV Successfully!")

# REQUIREMENT #2 - REVIEW STUDENT
@staff_cli.command("review", help="Adds A Review To A Student")
@click.argument("student_id", required=False)
@click.argument("text", nargs=-1, required=False)  # Used nargs=-1 To Accept Multiple Words As A Single Argument :D
@click.argument("reviewer_id", required=False)
def review_student_command(student_id, text, reviewer_id):
    if student_id is None:
        student_id = input("Enter Student ID To Review: ")

    if not text:
        text = input("Enter Review: ")
    else:
        text = " ".join(text)

    if reviewer_id is None:
        reviewer_id = input("Input Your Staff ID: ")

    review = add_review(student_id, text, reviewer_id)
    student = get_student(student_id)

    if review and student:
        print(f"Review Uploaded To Student With ID: {student_id} ({student.firstname} {student.lastname}) Successfully!")
    else:
        print(f"ERROR: Student With ID {student_id} Does Not Exist.")

# REQUIREMENT #3 - VIEW STUDENT REVIEWS
@staff_cli.command("view_student_reviews", help="List All Reviews For Specified Student")
@click.argument("student_id")
@click.argument("format", default="string")
def list_review_command(student_id, format):
    reviews = get_student_reviews(student_id)
    if reviews and format == "string":
        print(get_student_reviews(student_id))
    elif not reviews:
        print(f"ERROR: Student With ID {student_id} Does Not Exist.")
    else:
        print(get_student_reviews_json(student_id))

# REQUIREMENT #4 - SEARCH STUDENT
@staff_cli.command("search_student", help="Searches For Specific Student")
@click.argument("student_id", default="816032484")
def search_student_command(student_id):
    if get_student(student_id):
        print(search_student_by_student_id(student_id))
    else:
        print(f"ERROR: Student With ID {student_id} Does Not Exist.")

# EXTRA #3 - LIST ALL STUDENTS
@staff_cli.command("list_students", help="Lists All Student Records In The Database")
@click.argument("format", default="string")
def list_staff_command(format):
    if format == 'string':
        print(get_all_students())
    else:
        print(get_all_students_json())

app.cli.add_command(staff_cli)

'''
Test Commands
'''

test = AppGroup('test', help='Testing Commands') 

@test.command("staff", help="Run Staff tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))

app.cli.add_command(test)