from datetime import datetime
from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Boolean, Text, event
from sqlalchemy.orm import relationship


class Cliente(Model):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    direccion = Column(String(255), nullable=True)
    creado_en = Column(DateTime, default=datetime.now, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    vehiculos = relationship("Vehiculo", back_populates="cliente")

    def __repr__(self):
        return f"{self.nombre} {self.apellido}"


class Vehiculo(Model):
    __tablename__ = "vehiculo"

    id = Column(Integer, primary_key=True)
    placa = Column(String(20), nullable=False)
    marca = Column(String(100), nullable=False)
    modelo = Column(String(100), nullable=False)
    color = Column(String(50), nullable=True)

    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    cliente = relationship("Cliente", back_populates="vehiculos")

    ordenes = relationship("OrdenTrabajo", back_populates="vehiculo")

    creado_en = Column(DateTime, default=datetime.now, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"{self.placa} - {self.marca}"


class Servicio(Model):
    __tablename__ = "servicio"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Numeric(10, 2), nullable=False)
    estado = Column(Boolean, default=True)

    detalles = relationship("DetalleServicio", back_populates="servicio")

    creado_en = Column(DateTime, default=datetime.now, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return self.nombre


class OrdenTrabajo(Model):
    __tablename__ = "orden_trabajo"

    id = Column(Integer, primary_key=True)

    vehiculo_id = Column(Integer, ForeignKey("vehiculo.id"), nullable=False)
    vehiculo = relationship("Vehiculo", back_populates="ordenes")

    fecha_ingreso = Column(DateTime, default=datetime.now)
    estado = Column(String(50), default="Pendiente", nullable=False)
    total = Column(Numeric(10, 2), default=0, nullable=False)
    observacion = Column(Text, nullable=True)

    detalles = relationship("DetalleServicio", back_populates="orden")

    creado_en = Column(DateTime, default=datetime.now, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"Orden #{self.id}"


class DetalleServicio(Model):
    __tablename__ = "detalle_servicio"

    id = Column(Integer, primary_key=True)

    orden_id = Column(Integer, ForeignKey("orden_trabajo.id"), nullable=False)
    servicio_id = Column(Integer, ForeignKey("servicio.id"), nullable=False)

    cantidad = Column(Integer, default=1, nullable=False)
    subtotal = Column(Numeric(10, 2), default=0, nullable=False)

    orden = relationship("OrdenTrabajo", back_populates="detalles")
    servicio = relationship("Servicio", back_populates="detalles")

    def __repr__(self):
        return f"Detalle {self.id}"


def recalcular_total_orden(connection, orden_id):
    detalles = connection.execute(
        DetalleServicio.__table__.select().where(
            DetalleServicio.orden_id == orden_id
        )
    ).fetchall()

    total = 0

    for detalle in detalles:
        total += detalle.subtotal or 0

    connection.execute(
        OrdenTrabajo.__table__.update()
        .where(OrdenTrabajo.id == orden_id)
        .values(total=total)
    )


@event.listens_for(DetalleServicio, "before_insert")
def calcular_subtotal_insert(mapper, connection, target):
    servicio = connection.execute(
        Servicio.__table__.select().where(
            Servicio.id == target.servicio_id
        )
    ).fetchone()

    if servicio:
        target.subtotal = target.cantidad * servicio.precio


@event.listens_for(DetalleServicio, "before_update")
def calcular_subtotal_update(mapper, connection, target):
    servicio = connection.execute(
        Servicio.__table__.select().where(
            Servicio.id == target.servicio_id
        )
    ).fetchone()

    if servicio:
        target.subtotal = target.cantidad * servicio.precio


@event.listens_for(DetalleServicio, "after_insert")
def actualizar_total_insert(mapper, connection, target):
    recalcular_total_orden(connection, target.orden_id)


@event.listens_for(DetalleServicio, "after_update")
def actualizar_total_update(mapper, connection, target):
    recalcular_total_orden(connection, target.orden_id)


@event.listens_for(DetalleServicio, "after_delete")
def actualizar_total_delete(mapper, connection, target):
    recalcular_total_orden(connection, target.orden_id)