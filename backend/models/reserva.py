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

    # Estados: activa, en_progreso, completada, cancelada
    estado = db.Column(db.String(50), default="activa")

    # 🆕 NUEVOS CAMPOS PARA KIOSK
    hora_inicio_real = db.Column(db.DateTime, nullable=True)  # Cuando realmente llegó
    hora_fin_real = db.Column(db.DateTime, nullable=True)  # Cuando realmente terminó
    conector_id = db.Column(db.Integer, nullable=True)  # Qué conector usó
    duracion_real_horas = db.Column(
        db.Float, nullable=True
    )  # Duración real de la carga

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    codigo = db.Column(db.String(20), unique=True, nullable=False)

    # Relación con User
    user = db.relationship("User", backref=db.backref("reservas", lazy=True))

    def to_dict(self, include_user_info=False):
        """
        Convertir a diccionario con opción de incluir info del usuario
        """
        data = {
            "id": self.id,
            "codigo": self.codigo,
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
            # 🆕 Nuevos campos
            "hora_inicio_real": (
                self.hora_inicio_real.strftime("%Y-%m-%d %H:%M:%S")
                if self.hora_inicio_real
                else None
            ),
            "hora_fin_real": (
                self.hora_fin_real.strftime("%Y-%m-%d %H:%M:%S")
                if self.hora_fin_real
                else None
            ),
            "conector_id": self.conector_id,
            "duracion_real_horas": self.duracion_real_horas,
        }

        # Incluir info del usuario si se solicita (para el kiosk)
        if include_user_info and self.user:
            data["usuario"] = {
                "id": self.user.id,
                "username": self.user.username,
                "email": self.user.email,
                "phone": self.user.phone,
            }

        return data

    def __repr__(self):
        return f"<Reserva {self.id} - Estación {self.estacion_id} - Usuario {self.user_id} - Estado: {self.estado}>"
