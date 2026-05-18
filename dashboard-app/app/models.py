from .extensions import db


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))


class Vehiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(20), nullable=False)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"))


class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)


class OrdenTrabajo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(200))
    estado = db.Column(db.String(50))
    vehiculo_id = db.Column(db.Integer, db.ForeignKey("vehiculo.id"))


class DetalleServicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey("orden_trabajo.id"))
    servicio_id = db.Column(db.Integer, db.ForeignKey("servicio.id"))
    cantidad = db.Column(db.Integer, default=1)