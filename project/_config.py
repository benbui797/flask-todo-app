import os

# make path to folder of this file
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = "flasktaskr.db"
WTF_CSRF_ENABLED = True
SECRET_KEY = "b'V\xcd2@S\xe5\xc9M\xa3\xae\x14\x1b\xbbs9\xce4&\xd3\x87,\xd9\xc9\xa8'"
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = False

# define full path for database
DATABASE_PATH = os.path.join(basedir, DATABASE)

SQLALCHEMY_DATABASE_URI = "sqlite:///" + DATABASE_PATH
