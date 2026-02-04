# backend/models/estaciones.py

"""
Modelo Station (tabla: stations)

Esta tabla guarda estaciones de carga.
La idea es poder guardar datos que vienen de OpenChargeMap (Paraguay) en SQLite.
"""

from db import db  # Importamos la instancia de SQLAlchemy
from sqlalchemy.sql import func  # Para usar CURRENT_TIMESTAMP de la DB


class Station(db.Model):
    """
    Representa una estación de carga.
    """

    __tablename__ = "stations"  # Nombre exacto de la tabla en chargeway.db

    # -------------------------
    # Columnas (deben calzar con tu schema)
    # -------------------------

    # id: PK. Puedes usar el ID de OpenChargeMap como id, o dejar que autogenere.
    # Recomendación: usar el ID de OpenChargeMap para poder "upsert" (actualizar/insertar) sin duplicar.
    id = db.Column(db.Integer, primary_key=True)

    # Nombre de la estación
    nombre = db.Column(db.String(120), nullable=False)

    # Dirección de la estación (texto)
    direccion = db.Column(db.String(200), nullable=False)

    # Coordenadas (en tu tabla es lat y lon)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)

    # Fecha de creación (por defecto timestamp actual)
    created_at = db.Column(db.DateTime, server_default=func.current_timestamp())

    # -------------------------
    # Relaciones
    # -------------------------
    # Una estación puede tener muchos conectores
    # cascade: si borras estación, borra conectores asociados (útil si usas reset=True en sync)
    connectors = db.relationship(
        "Connector",
        backref="station",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def to_dict(self, include_connectors=False):
        """
        Convierte el objeto a dict para devolverlo por API.
        include_connectors=True incluye los conectores asociados.
        """
        data = {
            "id": self.id,
            "nombre": self.nombre,
            "direccion": self.direccion,
            "lat": self.lat,
            "lon": self.lon,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        if include_connectors:
            # Convertimos cada conector a dict
            data["connectors"] = [c.to_dict() for c in self.connectors]

        return data

    def __repr__(self):
        return f"<Station id={self.id} nombre={self.nombre}>"