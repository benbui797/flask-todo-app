import os
import unittest

from project import app, db, bcrypt
from project._config import basedir
from project.models import Task, User

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
            password=bcrypt.generate_password_hash(password).decode("utf-8")
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

    def create_admin_user(self):
        new_user = User(
            name="Superman",
            email="superman@kryptonite.com",
            password=bcrypt.generate_password_hash("allpowerful").decode("utf-8"),
            role="admin"
        )
        db.session.add(new_user)
        db.session.commit()


    ###############
    #### tests ####
    ###############

    def test_logged_in_users_can_acces_tasks_page(self):
        self.register("benbui2", "benbui2@hotmail.com", "benbui2", "benbui2")
        self.login("benbui2", "benbui2")
        response = self.app.get("tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Add a new task:", response.data)

    def test_not_logged_in_users_cannot_access_tasks_page(self):
        response = self.app.get("tasks/", follow_redirects=True)
        self.assertIn(b"You need to login first.", response.data)

    def test_users_can_add_tasks(self):
        self.create_user("benbui3", "benbui3@benbui.com", "benbui3")
        self.login("benbui3", "benbui3")
        self.app.get("tasks/", follow_redirects=True)
        response = self.create_task()
        self.assertIn(
            b"New entry was successfully posted. Thanks.", response.data
        )
    
    # This one doesn't work because html also checks for required fields
    """
    def test_users_cannot_add_tasks_when_error(self):
        self.create_user("benbui3", "benbui3@benbui.com", "benbui3")
        self.login("benbui3", "benbui3")
        self.app.get("tasks/", follow_redirects=True)
        response = self.app.post("add/", data=dict(
            name="Drink coffee",
            due_date="2022-04-10",
            priority="1",
            posted_date="2022-04-07",
            status="1"
        ), follow_redirects=True)
        self.assertIn(b"This field is required.", response.data)
    """

    def test_users_can_complete_tasks(self):
        self.create_user("benbui3", "benbui3@benbui.com", "benbui3")
        self.login("benbui3", "benbui3")
        self.app.get("tasks/", follow_redirects=True)
        self.create_task()
        response = self.app.get("complete/1", follow_redirects=True)
        self.assertIn(b"The task is complete. Nice.", response.data)
    
    def test_users_can_delete_tasks(self):
        self.create_user("benbui3", "benbui3@benbui.com", "benbui3")
        self.login("benbui3", "benbui3")
        self.app.get("tasks/", follow_redirects=True)
        self.create_task()
        response = self.app.get("delete/1", follow_redirects=True)
        self.assertIn(b"The task was deleted.", response.data)

    def test_users_cannot_complete_tasks_not_created_by_them(self):
        self.create_user("benbui3", "benbui3@benbui.com", "benbui3")
        self.login("benbui3", "benbui3")
        self.app.get("tasks/", follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user("benbui2", "benbui2@benbui.com", "benbui2")
        self.login("benbui2", "benbui2")
        self.app.get("tasks/", follow_redirects=True)
        response = self.app.get("complete/1", follow_redirects=True)
        self.assertNotIn(
            b"The task is completed. Well done!", response.data
        )
        self.assertIn(b"You can only update tasks that belong to you.", response.data)

    def test_users_cannot_delete_tasks_not_created_by_them(self):
        self.create_user("benbui3", "benbui3@benbui.com", "benbui3")
        self.login("benbui3", "benbui3")
        self.app.get("tasks/", follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user("benbui2", "benbui2@benbui.com", "benbui2")
        self.login("benbui2", "benbui2")
        self.app.get("tasks/", follow_redirects=True)
        response = self.app.get("delete/1", follow_redirects=True)
        self.assertIn(b"You can only delete tasks that belong to you.", response.data)
    
    def test_default_user_role(self):
        db.session.add(
            User(
            "BennyB",
            "bennyb@bennyb.com",
            "bennyb"
            )
        )
        db.session.commit()
        users = db.session.query(User).all()
        print(users)
        for user in users:
            self.assertEqual(user.role, "user")

    def test_admin_users_can_complete_tasks_not_created_by_them(self):
        self.create_user("benbui3", "benbui3@benbui.com", "benbui3")
        self.login("benbui3", "benbui3")
        self.app.get("tasks/", follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login("Superman", "allpowerful")
        self.app.get("tasks/", follow_redirects=True)
        response = self.app.get("complete/1", follow_redirects=True)
        self.assertNotIn(
            b"You can only update tasks that belong to you.", response.data
        )
    
    def test_admin_users_can_delete_tasks_not_created_by_them(self):
        self.create_user("benbui3", "benbui3@benbui.com", "benbui3")
        self.login("benbui3", "benbui3")
        self.app.get("tasks/", follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login("Superman", "allpowerful")
        self.app.get("tasks/", follow_redirects=True)
        response = self.app.get("delete/1", follow_redirects=True)
        self.assertNotIn(
            b"You can only delete tasks that belong to you.", response.data
        )

    def test_users_cannot_see_task_modify_links_without_permission(self):
        self.create_user("benbui2", "benbui2@benbui.com", "benbui2")
        self.login("benbui2", "benbui2")
        self.app.get("tasks/", follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user("benbui3", "benbui3@benbui.com", "benbui3")
        response = self.login("benbui3", "benbui3")
        self.app.get("tasks/", follow_redirects=True)
        self.assertNotIn(b"Mark as complete", response.data)
        self.assertNotIn(b"Delete", response.data)

    def test_users_can_see_task_modify_links_with_permission(self):
        self.create_user("benbui2", "benbui2@benbui.com", "benbui2")
        self.login("benbui2", "benbui2")
        self.app.get("tasks/", follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user("benbui3", "benbui3@benbui.com", "benbui3")
        self.login("benbui3", "benbui3")
        self.app.get("tasks/", follow_redirects=True)
        response = self.create_task()
        self.assertIn(b"complete/2", response.data)
        self.assertIn(b"delete/2", response.data)
    
    def test_admins_can_see_modify_links_for_all_tasks(self):
        self.create_user("benbui2", "benbui2@benbui.com", "benbui2")
        self.login("benbui2", "benbui2")
        self.app.get("tasks/", follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login("Superman", "allpowerful")
        self.app.get("tasks/", follow_redirects=True)
        response = self.create_task()
        self.assertIn(b"complete/1", response.data)
        self.assertIn(b"delete/1", response.data)
        self.assertIn(b"complete/2", response.data)
        self.assertIn(b"delete/2", response.data)
    
if __name__ == "__main__":
    unittest.main()
  