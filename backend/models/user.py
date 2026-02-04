from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from db import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    # ============================================
    # 🆕 NUEVO: Sistema de Roles
    # ============================================
    role = db.Column(db.String(20), default="user", nullable=False)
    # Valores posibles: 'user', 'admin'

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ============================================
    # 🆕 NUEVOS MÉTODOS PARA ROLES
    # ============================================
    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.role == "admin"

    def to_dict(self, include_role=False):
        """Convertir usuario a diccionario para JSON"""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "is_active": self.is_active,
            "created_at": (
                self.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.created_at
                else None
            ),
        }

        if include_role:
            data["role"] = self.role
            data["is_admin"] = self.is_admin()

        return data
