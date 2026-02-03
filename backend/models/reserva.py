from datetime import datetime
from db import db


class Reserva(db.Model):
    __tablename__ = "reservas"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    estacion_id = db.Column(db.Integer, nullable=False)
    estacion_nombre = db.Column(db.String(200))
    estacion_direccion = db.Column(db.String(300))
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    duracion_horas = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(50), default="activa")  # activa, completada, cancelada
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relación con User
    user = db.relationship("User", backref=db.backref("reservas", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "estacion_id": self.estacion_id,
            "estacion_nombre": self.estacion_nombre,
            "estacion_direccion": self.estacion_direccion,
            "fecha": self.fecha.strftime("%Y-%m-%d") if self.fecha else None,
            "hora_inicio": (
                self.hora_inicio.strftime("%H:%M") if self.hora_inicio else None
            ),
            "duracion_horas": self.duracion_horas,
            "estado": self.estado,
            "created_at": (
                self.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.created_at
                else None
            ),
            "updated_at": (
                self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.updated_at
                else None
            ),
        }

    def __repr__(self):
        return f"<Reserva {self.id} - Estación {self.estacion_id} - Usuario {self.user_id}>"
