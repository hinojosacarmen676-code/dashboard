from io import BytesIO

from flask import render_template, request, send_file
from flask_appbuilder import BaseView, ModelView, expose, has_access
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy import func
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .extensions import appbuilder, db
from .models import Cliente, Vehiculo, Servicio, OrdenTrabajo, DetalleServicio


class DashboardGeneralView(BaseView):
    route_base = "/dashboard-general"
    default_view = "index"

    @expose("/")
    @has_access
    def index(self):
        estado = request.args.get("estado", "")
        fecha_desde = request.args.get("fecha_desde", "")
        fecha_hasta = request.args.get("fecha_hasta", "")

        ordenes_query = db.session.query(OrdenTrabajo)

        if estado:
            ordenes_query = ordenes_query.filter(OrdenTrabajo.estado == estado)

        if fecha_desde:
            ordenes_query = ordenes_query.filter(OrdenTrabajo.fecha_ingreso >= fecha_desde)

        if fecha_hasta:
            ordenes_query = ordenes_query.filter(OrdenTrabajo.fecha_ingreso <= fecha_hasta)

        ordenes = ordenes_query.all()

        total_clientes = db.session.query(func.count(Cliente.id)).scalar() or 0
        total_vehiculos = db.session.query(func.count(Vehiculo.id)).scalar() or 0
        total_ordenes = len(ordenes)
        total_ingresos = sum(float(o.total or 0) for o in ordenes)

        servicios = (
            db.session.query(Servicio.nombre, func.count(DetalleServicio.id))
            .join(DetalleServicio)
            .group_by(Servicio.nombre)
            .order_by(func.count(DetalleServicio.id).desc())
            .all()
        )

        nombres = [s[0] for s in servicios]
        cantidades = [s[1] for s in servicios]

        servicio_top = nombres[0] if nombres else "Sin datos"

        analisis_ia = (
            f"Análisis automático generado por IA: el sistema registra {total_clientes} clientes, "
            f"{total_vehiculos} vehículos y {total_ordenes} órdenes de trabajo. "
            f"Los ingresos actuales son Bs. {total_ingresos:.2f}. "
            f"El servicio con mayor demanda es {servicio_top}. "
            f"Se recomienda organizar materiales, herramientas y personal técnico según la demanda."
        )
  

        return self.render_template(
            "dashboard_general.html",
            total_clientes=total_clientes,
            total_vehiculos=total_vehiculos,
            total_ordenes=total_ordenes,
            total_ingresos=f"{total_ingresos:.2f}",
            nombres=nombres,
            cantidades=cantidades,
            analisis_ia=analisis_ia,
            estado=estado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )


class DashboardPDFView(BaseView):
    route_base = "/exportar-pdf"
    default_view = "index"

    @expose("/")
    @has_access
    def index(self):
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        total_clientes = db.session.query(func.count(Cliente.id)).scalar() or 0
        total_vehiculos = db.session.query(func.count(Vehiculo.id)).scalar() or 0
        total_ordenes = db.session.query(func.count(OrdenTrabajo.id)).scalar() or 0
        total_ingresos = db.session.query(func.sum(OrdenTrabajo.total)).scalar() or 0

        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(50, 760, "Reporte Inteligente del Taller Mecánico")

        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, 710, f"Clientes registrados: {total_clientes}")
        pdf.drawString(50, 690, f"Vehículos registrados: {total_vehiculos}")
        pdf.drawString(50, 670, f"Órdenes de trabajo: {total_ordenes}")
        pdf.drawString(50, 650, f"Ingresos totales: Bs. {float(total_ingresos):.2f}")

        pdf.drawString(50, 610, "Modelo utilizado:")
        pdf.drawString(50, 590, "IA basada en reglas inteligentes y análisis de datos históricos.")

        pdf.drawString(50, 550, "Resultado:")
        pdf.drawString(50, 530, "El sistema genera recomendaciones automáticas para apoyar")
        pdf.drawString(50, 510, "la toma de decisiones del taller mecánico.")

        pdf.save()
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name="reporte_inteligente_taller.pdf",
            mimetype="application/pdf",
        )


class HistorialVehiculoView(BaseView):
    route_base = "/historial-vehiculo"
    default_view = "index"

    @expose("/")
    @has_access
    def index(self):
        vehiculo_id = request.args.get("vehiculo_id", "")

        vehiculos = db.session.query(Vehiculo).all()
        vehiculo = None
        ordenes = []

        if vehiculo_id:
            vehiculo = db.session.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
            if vehiculo:
                ordenes = vehiculo.ordenes

        return self.render_template(
            "historial_vehiculo.html",
            vehiculos=vehiculos,
            vehiculo=vehiculo,
            ordenes=ordenes,
            vehiculo_id=vehiculo_id,
        )


class ClienteView(ModelView):
    datamodel = SQLAInterface(Cliente)
    list_columns = ["nombre", "apellido", "telefono", "direccion"]
    add_columns = ["nombre", "apellido", "telefono", "direccion"]
    edit_columns = ["nombre", "apellido", "telefono", "direccion"]
    search_columns = ["nombre", "apellido"]
    base_order = ("nombre", "asc")


class VehiculoView(ModelView):
    datamodel = SQLAInterface(Vehiculo)
    list_columns = ["placa", "marca", "modelo", "color", "cliente"]
    add_columns = ["placa", "marca", "modelo", "color", "cliente"]
    edit_columns = ["placa", "marca", "modelo", "color", "cliente"]
    search_columns = ["placa", "marca", "modelo"]
    base_order = ("placa", "asc")


class ServicioView(ModelView):
    datamodel = SQLAInterface(Servicio)
    list_columns = ["nombre", "descripcion", "precio", "estado"]
    add_columns = ["nombre", "descripcion", "precio", "estado"]
    edit_columns = ["nombre", "descripcion", "precio", "estado"]
    search_columns = ["nombre"]
    base_order = ("nombre", "asc")


class OrdenTrabajoView(ModelView):
    datamodel = SQLAInterface(OrdenTrabajo)
    list_columns = ["vehiculo", "fecha_ingreso", "estado", "total", "observacion"]
    add_columns = ["vehiculo", "estado", "observacion"]
    edit_columns = ["vehiculo", "estado", "observacion"]
    search_columns = ["estado"]
    base_order = ("fecha_ingreso", "desc")

    label_columns = {
        "vehiculo": "Vehículo",
        "fecha_ingreso": "Fecha",
        "estado": "Estado",
        "total": "Total",
        "observacion": "Observación",
    }


class DetalleServicioView(ModelView):
    datamodel = SQLAInterface(DetalleServicio)
    list_columns = ["orden", "servicio", "cantidad", "precio_unitario", "subtotal"]
    add_columns = ["orden", "servicio", "cantidad"]
    edit_columns = ["orden", "servicio", "cantidad"]


def ia_tendencias(servicio_top, cliente_top):
    texto = "El análisis inteligente detecta patrones importantes en el comportamiento del taller. "

    if servicio_top:
        texto += f"El servicio con mayor demanda es {servicio_top}. "
    else:
        texto += "Aún no existen suficientes servicios registrados. "

    if cliente_top:
        texto += f"El cliente más frecuente es {cliente_top}. "
    else:
        texto += "Aún no se identifica un cliente frecuente. "

    texto += (
        "Se recomienda fidelizar clientes, reforzar servicios principales y promocionar "
        "servicios con baja demanda para equilibrar el rendimiento del taller."
    )

    return texto


def ia_recomendacion(servicio_top, total_ingresos):
    if not servicio_top:
        return "No existen suficientes datos para generar recomendaciones inteligentes."

    texto = (
        f"El modelo inteligente recomienda fortalecer el servicio de {servicio_top}, "
        f"porque presenta mayor demanda dentro del sistema. "
    )

    if float(total_ingresos or 0) >= 1000:
        texto += (
            "Los ingresos son positivos, por lo que se recomienda ampliar la capacidad "
            "de atención y crear paquetes de mantenimiento preventivo. "
        )
    else:
        texto += (
            "Los ingresos aún son bajos, por lo que se recomienda aplicar promociones "
            "y estrategias de captación de clientes. "
        )

    texto += (
        f"Predicción estimada: el servicio {servicio_top} continuará siendo uno de los más "
        f"solicitados en las próximas atenciones del taller."
    )

    return texto


class ReporteTendenciasIAView(BaseView):
    route_base = "/reporte_tendencias_ia"
    default_view = "index"

    @expose("/")
    @has_access
    def index(self):
        servicios = (
            db.session.query(Servicio.nombre, func.count(DetalleServicio.id))
            .join(DetalleServicio)
            .group_by(Servicio.nombre)
            .order_by(func.count(DetalleServicio.id).desc())
            .all()
        )

        clientes = (
            db.session.query(Cliente.nombre, func.count(OrdenTrabajo.id))
            .join(Vehiculo, Cliente.id == Vehiculo.cliente_id)
            .join(OrdenTrabajo, Vehiculo.id == OrdenTrabajo.vehiculo_id)
            .group_by(Cliente.nombre)
            .order_by(func.count(OrdenTrabajo.id).desc())
            .all()
        )

        servicios_nombres = [s[0] for s in servicios]
        servicios_cantidades = [s[1] for s in servicios]
        clientes_nombres = [c[0] for c in clientes]
        clientes_cantidades = [c[1] for c in clientes]

        servicio_top = servicios_nombres[0] if servicios_nombres else None
        cliente_top = clientes_nombres[0] if clientes_nombres else None

        analisis_ia = ia_tendencias(servicio_top, cliente_top)

        return self.render_template(
            "reporte_tendencias_ia.html",
            servicios_nombres=servicios_nombres,
            servicios_cantidades=servicios_cantidades,
            clientes_nombres=clientes_nombres,
            clientes_cantidades=clientes_cantidades,
            analisis_ia=analisis_ia,
        )


class ReporteRecomendacionIAView(BaseView):
    route_base = "/reporte_recomendacion_ia"
    default_view = "index"

    @expose("/")
    @has_access
    def index(self):
        total_ingresos = db.session.query(func.sum(DetalleServicio.subtotal)).scalar() or 0

        servicios = (
            db.session.query(Servicio.nombre, func.count(DetalleServicio.id))
            .join(DetalleServicio)
            .group_by(Servicio.nombre)
            .order_by(func.count(DetalleServicio.id).desc())
            .all()
        )

        nombres = [s[0] for s in servicios]
        cantidades = [s[1] for s in servicios]
        servicio_top = nombres[0] if nombres else None

        recomendacion_ia = ia_recomendacion(servicio_top, total_ingresos)

        return self.render_template(
            "reporte_recomendacion_ia.html",
            nombres=nombres,
            cantidades=cantidades,
            total_ingresos=f"{float(total_ingresos or 0):.2f}",
            recomendacion_ia=recomendacion_ia,
            servicio_top=servicio_top,
        )


class ReporteRecomendacionIAView(BaseView):
    route_base = "/reporte_recomendacion_ia"
    default_view = "index"

    @expose("/")
    @has_access
    def index(self):
        total_ingresos = db.session.query(func.sum(DetalleServicio.subtotal)).scalar() or 0

        servicios = (
            db.session.query(Servicio.nombre, func.count(DetalleServicio.id))
            .join(DetalleServicio)
            .group_by(Servicio.nombre)
            .order_by(func.count(DetalleServicio.id).desc())
            .all()
        )

        nombres = [s[0] for s in servicios]
        cantidades = [s[1] for s in servicios]
        servicio_top = nombres[0] if nombres else None

        recomendacion_ia = ia_recomendacion(servicio_top, total_ingresos)

        return self.render_template(
            "reporte_recomendacion_ia.html",
            nombres=nombres,
            cantidades=cantidades,
            total_ingresos=f"{float(total_ingresos or 0):.2f}",
            recomendacion_ia=recomendacion_ia,
            servicio_top=servicio_top,
        )

appbuilder.add_view(ClienteView, "Clientes", icon="fa-user", category="Gestión Taller")
appbuilder.add_view(VehiculoView, "Vehículos", icon="fa-car", category="Gestión Taller")
appbuilder.add_view(ServicioView, "Servicios", icon="fa-wrench", category="Gestión Taller")
appbuilder.add_view(OrdenTrabajoView, "Órdenes", icon="fa-list", category="Gestión Taller")
appbuilder.add_view(DetalleServicioView, "Detalle Servicio", icon="fa-table", category="Gestión Taller")

appbuilder.add_view(DashboardGeneralView, "Reporte 1 - General", icon="fa-dashboard", category="Reportes Inteligentes")
appbuilder.add_view(ReporteTendenciasIAView, "Reporte 2 - Tendencias", icon="fa-line-chart", category="Reportes Inteligentes")
appbuilder.add_view(ReporteRecomendacionIAView, "Reporte 3 - Recomendación IA", icon="fa-lightbulb-o", category="Reportes Inteligentes")
appbuilder.add_view(DashboardPDFView, "Exportar PDF", icon="fa-file-pdf-o", category="Reportes Inteligentes")
appbuilder.add_view(HistorialVehiculoView, "Historial Vehículo", icon="fa-car", category="Reportes Inteligentes")