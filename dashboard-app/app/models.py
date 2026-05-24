from datetime import datetime
from decimal import Decimal

from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Boolean, Text, event
from sqlalchemy.orm import relationship


class Cliente(Model):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(20))
    direccion = Column(String(255))
    creado_en = Column(DateTime, default=datetime.now, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    vehiculos = relationship("Vehiculo", back_populates="cliente", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.nombre} {self.apellido}"


class Vehiculo(Model):
    __tablename__ = "vehiculo"

    id = Column(Integer, primary_key=True)
    placa = Column(String(20), nullable=False, unique=True)
    marca = Column(String(100), nullable=False)
    modelo = Column(String(100), nullable=False)
    color = Column(String(50))
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    creado_en = Column(DateTime, default=datetime.now, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    cliente = relationship("Cliente", back_populates="vehiculos")
    ordenes = relationship("OrdenTrabajo", back_populates="vehiculo", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.placa} - {self.marca} {self.modelo}"


class Servicio(Model):
    __tablename__ = "servicio"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    precio = Column(Numeric(10, 2), nullable=False)
    estado = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime, default=datetime.now, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    detalles = relationship("DetalleServicio", back_populates="servicio")

    def __repr__(self):
        return self.nombre


class OrdenTrabajo(Model):
    __tablename__ = "orden_trabajo"

    id = Column(Integer, primary_key=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculo.id"), nullable=False)
    fecha_ingreso = Column(DateTime, default=datetime.now, nullable=False)
    estado = Column(String(50), default="Pendiente", nullable=False)
    total = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    observacion = Column(Text)
    creado_en = Column(DateTime, default=datetime.now, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    vehiculo = relationship("Vehiculo", back_populates="ordenes")
    detalles = relationship("DetalleServicio", back_populates="orden", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Orden #{self.id} - {self.estado}"


class DetalleServicio(Model):
    __tablename__ = "detalle_servicio"

    id = Column(Integer, primary_key=True)
    orden_id = Column(Integer, ForeignKey("orden_trabajo.id"), nullable=False)
    servicio_id = Column(Integer, ForeignKey("servicio.id"), nullable=False)
    cantidad = Column(Integer, default=1, nullable=False)
    precio_unitario = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    subtotal = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)

    orden = relationship("OrdenTrabajo", back_populates="detalles")
    servicio = relationship("Servicio", back_populates="detalles")

    def __repr__(self):
        return f"{self.servicio} x {self.cantidad}"


def calcular_subtotal(target):
    if target.servicio:
        target.precio_unitario = Decimal(target.servicio.precio or 0)
        target.subtotal = Decimal(target.cantidad or 0) * Decimal(target.servicio.precio or 0)


def actualizar_total_orden(connection, orden_id):
    detalle_table = DetalleServicio.__table__
    orden_table = OrdenTrabajo.__table__

    result = connection.execute(
        detalle_table.select().where(detalle_table.c.orden_id == orden_id)
    )

    total = Decimal("0.00")

    for row in result:
        total += Decimal(row.subtotal or 0)

    connection.execute(
        orden_table.update()
        .where(orden_table.c.id == orden_id)
        .values(total=total)
    )


@event.listens_for(DetalleServicio, "before_insert")
def before_insert_detalle(mapper, connection, target):
    calcular_subtotal(target)


@event.listens_for(DetalleServicio, "before_update")
def before_update_detalle(mapper, connection, target):
    calcular_subtotal(target)


@event.listens_for(DetalleServicio, "after_insert")
def after_insert_detalle(mapper, connection, target):
    actualizar_total_orden(connection, target.orden_id)


@event.listens_for(DetalleServicio, "after_update")
def after_update_detalle(mapper, connection, target):
    actualizar_total_orden(connection, target.orden_id)


@event.listens_for(DetalleServicio, "after_delete")
def after_delete_detalle(mapper, connection, target):
    actualizar_total_orden(connection, target.orden_id)