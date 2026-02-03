from flask import Blueprint, jsonify, request, session
from db import db
from models.vehiculos import Auto
from models.user_vehiculo import UserVehiculo

vehiculos_bp = Blueprint("vehiculos_bp", __name__, url_prefix="/api")


@vehiculos_bp.route("/autos/", methods=["GET"])
def get_autos():
    """Obtener todos los autos disponibles"""
    try:
        autos = Auto.query.order_by(Auto.marca, Auto.modelo).all()
        return jsonify([auto.to_dict() for auto in autos]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vehiculos_bp.route("/mis-vehiculos/", methods=["GET"])
def get_mis_vehiculos():
    """Obtener vehículos del usuario actual"""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        vehiculos = (
            db.session.query(UserVehiculo, Auto)
            .join(Auto, UserVehiculo.auto_id == Auto.id)
            .filter(UserVehiculo.user_id == session["user_id"])
            .order_by(UserVehiculo.created_at.desc())
            .all()
        )
        
        result = []
        for user_vehiculo, auto in vehiculos:
            vehiculo_data = auto.to_dict()
            vehiculo_data['id'] = user_vehiculo.id  # ID de la relación, no del auto
            vehiculo_data['created_at'] = user_vehiculo.created_at.strftime('%d/%m/%Y %H:%M')
            result.append(vehiculo_data)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vehiculos_bp.route("/mis-vehiculos/", methods=["POST"])
def add_vehiculo():
    """Agregar vehículo al usuario"""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        data = request.get_json()
        auto_id = data.get('auto_id')
        
        if not auto_id:
            return jsonify({"error": "auto_id es requerido"}), 400
        
        # Verificar que el auto existe
        auto = Auto.query.get(auto_id)
        if not auto:
            return jsonify({"error": "Auto no encontrado"}), 404
        
        # Verificar que el usuario no tenga ya este auto
        existe = UserVehiculo.query.filter_by(
            user_id=session["user_id"],
            auto_id=auto_id
        ).first()
        
        if existe:
            return jsonify({"error": "Ya tienes este vehículo registrado"}), 400
        
        # Crear la relación
        user_vehiculo = UserVehiculo(
            user_id=session["user_id"],
            auto_id=auto_id
        )
        
        db.session.add(user_vehiculo)
        db.session.commit()
        
        return jsonify({"message": "Vehículo agregado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@vehiculos_bp.route("/mis-vehiculos/<int:vehiculo_id>", methods=["DELETE"])
def delete_vehiculo(vehiculo_id):
    """Eliminar vehículo del usuario"""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        vehiculo = UserVehiculo.query.filter_by(
            id=vehiculo_id,
            user_id=session["user_id"]
        ).first()
        
        if not vehiculo:
            return jsonify({"error": "Vehículo no encontrado"}), 404
        
        db.session.delete(vehiculo)
        db.session.commit()
        
        return jsonify({"message": "Vehículo eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500