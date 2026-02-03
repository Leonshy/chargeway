from db import db
from datetime import datetime


class Auto(db.Model):
    __tablename__ = 'autos'
    
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    año = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(50))
    bateria_kwh = db.Column(db.Float)
    autonomia_km = db.Column(db.Integer)
    potencia_hp = db.Column(db.Integer)
    consumo_est_kwh_100km = db.Column(db.Float)
    puerto_de_carga = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'marca': self.marca,
            'modelo': self.modelo,
            'año': self.año,
            'tipo': self.tipo,
            'bateria_kwh': self.bateria_kwh,
            'autonomia_km': self.autonomia_km,
            'potencia_hp': self.potencia_hp,
            'consumo_est_kwh_100km': self.consumo_est_kwh_100km,
            'puerto_de_carga': self.puerto_de_carga
        }