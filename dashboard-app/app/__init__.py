from flask import Flask
from .extensions import appbuilder, db


def create_app():
    app = Flask(__name__)

    app.config.from_object("config")

    db.init_app(app)

    with app.app_context():
        from . import models

        appbuilder.init_app(app, db.session)

        from . import views

        db.create_all()

    return app


app = create_app()