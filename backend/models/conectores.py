"""
Modelo Connector (tabla: connectors)

Esta tabla guarda conectores individuales por estación.
Las reservas se harán a nivel conector (como definieron en el proyecto).
"""

from db import db
from sqlalchemy.sql import func


class Connector(db.Model):
    """
    Representa un conector de carga asociado a una estación.
    """

    __tablename__ = "connectors"

    # -------------------------
    # Columnas
    # -------------------------

    # id: PK. Puedes usar el ID del "Connection" de OpenChargeMap si existe.
    # Si no existe, autoincrement.
    id = db.Column(db.Integer, primary_key=True)

    # FK a stations.id (en tu schema se llama estacion_id)
    estacion_id = db.Column(
        db.Integer,
        db.ForeignKey("stations.id"),
        nullable=False
    )

    # Nombre interno o etiqueta del conector (ej: "Conector AC-01")
    nombre = db.Column(db.String(120), nullable=False)

    # Tipo de conector (ej: Type2, CCS, CHAdeMO, etc.)
    tipo = db.Column(db.String(80), nullable=True)

    # Potencia en kW (en tu schema es potencia_kw)
    potencia_kw = db.Column(db.Float, nullable=False, default=0.0)

    # Estado activo/inactivo (para poder desactivar conectores si querés)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    # Timestamp de creación
    created_at = db.Column(db.DateTime, server_default=func.current_timestamp())

    def to_dict(self):
        """
        Convierte el conector a dict para devolverlo por API.
        """
        return {
            "id": self.id,
            "estacion_id": self.estacion_id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "potencia_kw": self.potencia_kw,
            "activo": self.activo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Connector id={self.id} estacion_id={self.estacion_id} nombre={self.nombre}>"
