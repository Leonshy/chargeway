from datetime import datetime
from db import db

class Connector(db.Model):
    """
    Modelo Connector
    ----------------
    Representa un punto físico de carga dentro de una estación.

    ⚠️ Importante:
    - Modelo SOLO estructural
    - No se conecta todavía con reservas
    - No usa ForeignKey para no acoplar
    """

    __tablename__ = "connectors"

    # Clave primaria interna
    id = db.Column(db.Integer, primary_key=True)

    # ID lógico de la estación (sin FK estricta)
    estacion_id = db.Column(db.Integer, nullable=False)

    # Nombre o código visible del conector
    nombre = db.Column(db.String(50), nullable=False)

    # Tipo de conector: AC, DC, CCS, CHAdeMO, etc.
    tipo = db.Column(db.String(20), nullable=False)

    # Potencia del conector en kilovatios
    potencia_kw = db.Column(db.Float, nullable=False)

    # Estado del conector (activo / inactivo)
    activo = db.Column(db.Boolean, default=True)

    # Fecha de creación
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """
        Devuelve el conector en formato diccionario
        para ser usado en respuestas JSON.
        """
        return {
            "id": self.id,
            "estacion_id": self.estacion_id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "potencia_kw": self.potencia_kw,
            "activo": self.activo,
            "created_at": self.created_at.isoformat()
        }