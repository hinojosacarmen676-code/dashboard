from flask import Flask
from .extensions import db, appbuilder


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "mi_clave_secreta"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///taller.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        appbuilder.init_app(app, db.session)

        from . import views

        db.create_all()

    return app
