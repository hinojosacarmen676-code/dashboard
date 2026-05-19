from flask import Flask

from .extensions import appbuilder, db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")

    db.init_app(app)

    with app.app_context():

        # importar modelos
        from .models import (
            Cliente,
            Vehiculo,
            Servicio,
            OrdenTrabajo,
            DetalleServicio
        )

        # crear tablas
        db.create_all()

        # iniciar AppBuilder
        appbuilder.init_app(app, db.session)

        # importar vistas
        from . import views

    return app


app = create_app()