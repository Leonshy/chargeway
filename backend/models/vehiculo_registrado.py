# models/vehiculo_registrado.py
from db import db

class VehiculoRegistrado(db.Model):
    __tablename__ = 'vehiculos_registrados'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    autos_id = db.Column(db.Integer, db.ForeignKey('autos.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relación para acceder a los datos del auto fácilmente
    auto = db.relationship("Auto", backref="registros")