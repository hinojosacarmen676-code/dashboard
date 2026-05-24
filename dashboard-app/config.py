import os
from flask_appbuilder.security.manager import AUTH_DB

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = "aquilacontraseñasegura2026"

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/taller_mecanico"

SQLALCHEMY_TRACK_MODIFICATIONS = False

CSRF_ENABLED = True
AUTH_TYPE = AUTH_DB

BABEL_DEFAULT_LOCALE = "es"

LANGUAGES = {
    "en": {"flag": "gb", "name": "English"},
    "es": {"flag": "es", "name": "Spanish"},
}

UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
IMG_UPLOAD_FOLDER = UPLOAD_FOLDER
IMG_UPLOAD_URL = "/static/uploads/"