from db import db
from datetime import datetime


class VehiculoRegistrado(db.Model):
    __tablename__ = 'vehiculos_registrados'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    autos_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'autos_id': self.autos_id,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M') if self.created_at else None
        }