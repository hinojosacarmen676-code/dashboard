from flask import render_template
from flask_appbuilder import ModelView, BaseView, expose, has_access
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy import func

from . import appbuilder, db
from .models import Cliente, Vehiculo, Servicio, OrdenTrabajo, DetalleServicio


class ClienteView(ModelView):
    datamodel = SQLAInterface(Cliente)
    list_columns = ["nombre", "telefono", "direccion"]


class VehiculoView(ModelView):
    datamodel = SQLAInterface(Vehiculo)
    list_columns = ["placa", "marca", "modelo", "cliente"]


class ServicioView(ModelView):
    datamodel = SQLAInterface(Servicio)
    list_columns = ["nombre", "descripcion", "precio"]


class OrdenTrabajoView(ModelView):
    datamodel = SQLAInterface(OrdenTrabajo)
    list_columns = ["fecha", "estado", "vehiculo", "total"]


class DetalleServicioView(ModelView):
    datamodel = SQLAInterface(DetalleServicio)
    list_columns = ["orden", "servicio", "cantidad", "subtotal"]


class ReporteView(BaseView):
    route_base = "/reportes"

    @expose("/")
    @has_access
    def index(self):
        ingresos = db.session.query(func.sum(OrdenTrabajo.total)).scalar() or 0

        servicios = (
            db.session.query(Servicio.nombre, func.count(DetalleServicio.id))
            .join(DetalleServicio)
            .group_by(Servicio.nombre)
            .all()
        )

        nombres = [s[0] for s in servicios]
        cantidades = [s[1] for s in servicios]

        return render_template(
            "reportes.html",
            ingresos=ingresos,
            nombres=nombres,
            cantidades=cantidades
        )


appbuilder.add_view(ClienteView, "Clientes", icon="fa-user", category="Gestión Taller")
appbuilder.add_view(VehiculoView, "Vehículos", icon="fa-car", category="Gestión Taller")
appbuilder.add_view(ServicioView, "Servicios", icon="fa-wrench", category="Gestión Taller")
appbuilder.add_view(OrdenTrabajoView, "Órdenes de Trabajo", icon="fa-list", category="Gestión Taller")
appbuilder.add_view(DetalleServicioView, "Detalle Servicio", icon="fa-table", category="Gestión Taller")

appbuilder.add_view_no_menu(ReporteView())
appbuilder.add_link("Reportes", href="/reportes/", icon="fa-bar-chart", category="Gestión Taller")