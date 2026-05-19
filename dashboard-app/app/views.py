from flask import render_template
from flask_appbuilder import ModelView, BaseView, expose, has_access
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy import func, extract
from wtforms import SelectField
from wtforms.validators import DataRequired

from . import appbuilder, db
from .models import Cliente, Vehiculo, Servicio, OrdenTrabajo, DetalleServicio


class ClienteView(ModelView):
    datamodel = SQLAInterface(Cliente)
    list_columns = ["nombre", "apellido", "telefono", "direccion"]
    add_columns = ["nombre", "apellido", "telefono", "direccion"]
    edit_columns = ["nombre", "apellido", "telefono", "direccion"]
    show_columns = ["nombre", "apellido", "telefono", "direccion", "creado_en", "actualizado_en"]


class VehiculoView(ModelView):
    datamodel = SQLAInterface(Vehiculo)
    list_columns = ["placa", "marca", "modelo", "color", "cliente"]
    add_columns = ["placa", "marca", "modelo", "color", "cliente"]
    edit_columns = ["placa", "marca", "modelo", "color", "cliente"]
    show_columns = ["placa", "marca", "modelo", "color", "cliente", "creado_en", "actualizado_en"]


class ServicioView(ModelView):
    datamodel = SQLAInterface(Servicio)
    list_columns = ["nombre", "descripcion", "precio", "estado"]
    add_columns = ["nombre", "descripcion", "precio", "estado"]
    edit_columns = ["nombre", "descripcion", "precio", "estado"]
    show_columns = ["nombre", "descripcion", "precio", "estado", "creado_en", "actualizado_en"]


class OrdenTrabajoView(ModelView):
    datamodel = SQLAInterface(OrdenTrabajo)

    list_columns = ["vehiculo", "fecha_ingreso", "estado", "total", "observacion"]

    add_columns = ["vehiculo", "fecha_ingreso", "estado", "observacion"]

    edit_columns = ["vehiculo", "fecha_ingreso", "estado", "observacion"]

    show_columns = [
        "vehiculo",
        "fecha_ingreso",
        "estado",
        "total",
        "observacion",
        "creado_en",
        "actualizado_en"
    ]

    add_form_extra_fields = {
        "estado": SelectField(
            "Estado",
            choices=[
                ("Pendiente", "Pendiente"),
                ("En proceso", "En proceso"),
                ("Finalizado", "Finalizado"),
                ("Entregado", "Entregado"),
                ("Cancelado", "Cancelado"),
            ],
            default="Pendiente",
            validators=[DataRequired()]
        )
    }

    edit_form_extra_fields = add_form_extra_fields


class DetalleServicioView(ModelView):
    datamodel = SQLAInterface(DetalleServicio)

    list_columns = ["orden", "servicio", "cantidad", "subtotal"]

    add_columns = ["orden", "servicio", "cantidad"]

    edit_columns = ["orden", "servicio", "cantidad"]

    show_columns = ["orden", "servicio", "cantidad", "subtotal"]


class ReporteView(BaseView):
    route_base = "/reportes"

    @expose("/")
    @has_access
    def index(self):
        ingresos = db.session.query(func.sum(OrdenTrabajo.total)).scalar() or 0

        servicios = (
            db.session.query(
                Servicio.nombre,
                func.sum(DetalleServicio.cantidad)
            )
            .join(DetalleServicio)
            .group_by(Servicio.nombre)
            .all()
        )

        vehiculos_mes = (
             db.session.query(
        func.count(OrdenTrabajo.id)
    )
    .all()
        )

        clientes_frecuentes = (
           db.session.query(
        Cliente.nombre,
        Cliente.apellido,
        func.count(OrdenTrabajo.id)
    )
    .join(Vehiculo, Cliente.id == Vehiculo.cliente_id)
    .join(OrdenTrabajo, Vehiculo.id == OrdenTrabajo.vehiculo_id)
    .group_by(Cliente.nombre, Cliente.apellido)
    .all()
        )

        nombres = [s[0] for s in servicios]
        cantidades = [int(s[1]) for s in servicios]

        return render_template(
            "reportes.html",
            ingresos=ingresos,
            servicios=servicios,
            vehiculos_mes=vehiculos_mes,
            clientes_frecuentes=clientes_frecuentes,
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