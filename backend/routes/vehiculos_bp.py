from flask import Blueprint, jsonify, request, session
from db import db
from models.vehiculos import Auto
from models.vehiculo_registrado import VehiculoRegistrado

vehiculos_bp = Blueprint("vehiculos_bp", __name__, url_prefix="/api")


@vehiculos_bp.route("/autos/", methods=["GET"])
def get_autos():
    """Obtener todos los autos disponibles"""
    try:
        autos = Auto.query.order_by(Auto.marca, Auto.modelo).all()
        return jsonify([auto.to_dict() for auto in autos]), 200
    except Exception as e:
        print(f"Error en get_autos: {e}")
        return jsonify({"error": str(e)}), 500


@vehiculos_bp.route("/mis-vehiculos/", methods=["GET"])
def get_mis_vehiculos():
    """Obtener vehículos registrados del usuario"""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        # Obtener los registros del usuario
        registrados = VehiculoRegistrado.query.filter_by(
            user_id=session["user_id"]
        ).order_by(VehiculoRegistrado.created_at.desc()).all()
        
        result = []
        for registro in registrados:
            # Buscar la info completa del auto
            auto = Auto.query.get(registro.autos_id)
            
            if auto:
                vehiculo_data = auto.to_dict()
                vehiculo_data['id'] = registro.id  # ID del registro
                vehiculo_data['created_at'] = registro.created_at.strftime('%d/%m/%Y %H:%M') if registro.created_at else None
                result.append(vehiculo_data)
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error en get_mis_vehiculos: {e}")
        return jsonify({"error": str(e)}), 500


@vehiculos_bp.route("/mis-vehiculos/", methods=["POST"])
def add_vehiculo():
    """Agregar vehículo al usuario"""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        data = request.get_json()
        autos_id = data.get('auto_id')
        
        if not autos_id:
            return jsonify({"error": "auto_id es requerido"}), 400
        
        # Verificar que el auto existe
        auto = Auto.query.get(autos_id)
        if not auto:
            return jsonify({"error": "Vehículo no encontrado"}), 404
        
        # Verificar que el usuario no lo tenga ya
        existe = VehiculoRegistrado.query.filter_by(
            user_id=session["user_id"],
            autos_id=autos_id
        ).first()
        
        if existe:
            return jsonify({"error": "Ya tienes este vehículo registrado"}), 400
        
        # Crear el registro
        registro = VehiculoRegistrado(
            user_id=session["user_id"],
            autos_id=autos_id
        )
        
        db.session.add(registro)
        db.session.commit()
        
        return jsonify({"message": "Vehículo agregado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error en add_vehiculo: {e}")
        return jsonify({"error": str(e)}), 500


@vehiculos_bp.route("/mis-vehiculos/<int:registro_id>", methods=["DELETE"])
def delete_vehiculo(registro_id):
    """Eliminar vehículo del usuario"""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        registro = VehiculoRegistrado.query.filter_by(
            id=registro_id,
            user_id=session["user_id"]
        ).first()
        
        if not registro:
            return jsonify({"error": "Vehículo no encontrado"}), 404
        
        db.session.delete(registro)
        db.session.commit()
        
        return jsonify({"message": "Vehículo eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error en delete_vehiculo: {e}")
        return jsonify({"error": str(e)}), 500