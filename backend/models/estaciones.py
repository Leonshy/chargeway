# backend/models/estaciones.py

from datetime import datetime
from db import db

class Station(db.Model):
    """
    Modelo Station
    --------------
    Representa una estación de carga eléctrica.
    Este modelo mapea la tabla existente 'stations'
    en la base de datos chargeway.db
    """

    __tablename__ = "stations"

    id = db.Column(db.Integer, primary_key=True)

    # ID proveniente de la API externa (OpenChargeMap)
    external_id = db.Column(db.Integer, unique=True, nullable=False)

    nombre = db.Column(db.String(120), nullable=False)

    direccion = db.Column(db.String(255), nullable=False)

    ciudad = db.Column(db.String(100))

    pais = db.Column(db.String(50), default="Paraguay")

    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)

    operador = db.Column(db.String(120))

    activo = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """
        Convierte el objeto Station en un diccionario
        para ser usado en APIs o respuestas JSON.
        """
        return {
            "id": self.id,
            "external_id": self.external_id,
            "nombre": self.nombre,
            "direccion": self.direccion,
            "ciudad": self.ciudad,
            "pais": self.pais,
            "lat": self.lat,
            "lng": self.lng,
            "operador": self.operador,
            "activo": self.activo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
