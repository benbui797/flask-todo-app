import os
import unittest

from project import app, db, bcrypt
from project._config import basedir
from project.models import User

TEST_DB = "test.db"


class AllTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

        self.assertEqual(app.debug, False)

    # executed after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()


    ########################
    #### helper methods ####
    ########################

    def login(self, name, password):
        return self.app.post("/", data=dict(
            name=name, password=password), follow_redirects=True)

    def register(self, name, email, password, confirm):
        return self.app.post(
            "register/",
            data=dict(name=name, email=email, password=password, confirm=confirm),
            follow_redirects=True
        )

    def logout(self):
        return self.app.get("logout/", follow_redirects=True)

    def create_user(self, name, email, password):
        new_user = User(
            name=name,
            email=email,
            password=bcrypt.generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

    def create_task(self):
        return self.app.post("add/", data=dict(
            name="Drink coffee",
            due_date="2022-04-10",
            priority="1",
            posted_date="2022-04-07",
            status="1"
        ), follow_redirects=True)


    ###############
    #### tests ####
    ###############

    # each test should start with 'test'
    def test_users_can_register(self):
        new_user = User("ben-bui", "benbuitendijk797@hotmail.com", bcrypt.generate_password_hash(
            "benbenbui"))
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()
        for t in test:
            t.name
        assert t.name == "ben-bui"

    def test_form_is_present_on_login_page(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please login to access your task list.", response.data)
    
    def test_users_cannot_login_unless_registered(self):
        response = self.login("foofoofoo", "barbarbar")
        self.assertIn(b"Invalid username or password", response.data)
    
    def test_users_can_login(self):
        self.register("Benbuit", "benbuitendijk797@hotmail.com", "benbui", "benbui")
        response = self.login("Benbuit", "benbui")
        self.assertIn(b"Welcome!", response.data)
    
    def test_invalid_form_data(self):
        self.register("BenBui", "benbuitendijk797@hotmail.com", "benbui", "benbui")
        response = self.login("alert('alert box!');", "foofoo")
        self.assertIn(b"Invalid username or password.", response.data)
    
    def test_form_is_present_on_register_page(self):
        response = self.app.get("register/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please register to access the task list.", response.data)
    
    def test_user_registration(self):
        self.app.get("register/", follow_redirects=True)
        response = self.register(
            "benbui", "benbuitendijk797@hotmail.com", "benben", "benben")
        self.assertIn(b"Thanks for registering. Please login.", response.data)

    def test_user_registration_error(self):
        self.app.get("register/", follow_redirects=True)
        self.register("Benbuit", "benbuitendijk797@hotmail.com", "benbui", "benbui")
        self.app.get("register/", follow_redirects=True)
        response = self.register(
            "Benbuit", "benbuitendijk797@hotmail.com", "benbui", "benbui"
        )
        self.assertIn(
            b"That username and/or email already exist.",
            response.data
        )
    
    def test_logged_in_users_can_logout(self):
        self.register("benbui2", "benbui2@hotmail.com", "benbui2", "benbui2")
        self.login("benbui2", "benbui2")
        response = self.logout()
        self.assertIn(b"Goodbye!", response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn(b"Goodbye!", response.data)

    def test_template_displays_user_name(self):
        self.register("benbui2", "benbui2@hotmail.com", "benbui2", "benbui2")
        self.login("benbui2", "benbui2")
        response = self.app.get("tasks/", follow_redirects=True)
        self.assertIn(b"benbui2", response.data)


    
if __name__ == "__main__":
    unittest.main()
  