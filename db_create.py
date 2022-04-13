from datetime import date

from project import db

from project.models import Task, User


# create the database and the db tables
db.create_all()

# insert data

# db.session.add(User("admin", "ad@min.com", "admin", "admin"))
# db.session.add(Task(
#     "Finish this tutorial", date(2022, 4, 7), 10, date(2022, 4, 9), 1, 1)
# )
# db.session.add(Task(
#     "Finish Real Python Course", date(2022, 4, 30), 10, date(2022, 4, 9), 1, 1)
# )

db.session.commit()
