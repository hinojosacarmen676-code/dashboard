import pymysql
import os
from flask_appbuilder.security.manager import (
    AUTH_REMOTE_USER,
    AUTH_DB,
    AUTH_LDAP,
    AUTH_OAUTH,
)

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = "aquilacontraseñasegura2026"

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/taller_mecanico"

CSRF_ENABLED = True

SQLALCHEMY_TRACK_MODIFICATIONS = False

AUTH_TYPE = AUTH_DB

BABEL_DEFAULT_LOCALE = "en"
BABEL_DEFAULT_FOLDER = "translations"

LANGUAGES = {
    "en": {"flag": "gb", "name": "English"},
    "es": {"flag": "es", "name": "Spanish"},
}

UPLOAD_FOLDER = basedir + "/app/static/uploads/"
IMG_UPLOAD_FOLDER = basedir + "/app/static/uploads/"
IMG_UPLOAD_URL = "/static/uploads/"