from datetime import datetime
from db import db


class UserVehiculo(db.Model):
    __tablename__ = 'user_vehiculos'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    auto_id = db.Column(db.Integer, db.ForeignKey('autos.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    user = db.relationship('User', backref='vehiculos')
    auto = db.relationship('Auto', backref='usuarios')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'auto_id': self.auto_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
