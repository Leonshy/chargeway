from flask import Blueprint, jsonify, request, session
from db import db
from models.vehiculos import Auto
from models.vehiculo_registrado import VehiculoRegistrado
from datetime import datetime

# Mantenemos el prefix /api para que las rutas sean /api/mis-vehiculos/ etc.
vehiculos_bp = Blueprint("vehiculos_bp", __name__, url_prefix="/api")

# --- LISTAR VEHÍCULOS DEL PANEL ---
@vehiculos_bp.route("/autos/", methods=["GET"])
def get_autos():
    try:
        autos = Auto.query.order_by(Auto.marca, Auto.modelo).all()
        return jsonify([auto.to_dict() for auto in autos]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@vehiculos_bp.route("/mis-vehiculos/", methods=["GET"])
def get_mis_vehiculos():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "No autenticado"}), 401
    try:
        registrados = VehiculoRegistrado.query.filter_by(user_id=user_id)\
            .order_by(VehiculoRegistrado.created_at.desc()).all()
        result = []
        for r in registrados:
            if r.auto:
                data = r.auto.to_dict()
                data["id_registro"] = r.id # IMPORTANTE: el ID de la tabla vehiculos_registrados
                data["fecha_registro"] = r.created_at
                result.append(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ======================================================
# 🚀 RUTA DE ELIMINACIÓN (CORRECCIÓN DEL 404)
# ======================================================
@vehiculos_bp.route("/mis-vehiculos/<int:id>", methods=["DELETE"])
@vehiculos_bp.route("/mis-vehiculos/<int:id>/", methods=["DELETE"])
def delete_vehiculo(id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "No autenticado"}), 401

    try:
        print(f"delete_vehiculo called - user_id={user_id} id={id}")
        # Primero intentamos por ID del registro
        registro = VehiculoRegistrado.query.filter_by(id=id, user_id=user_id).first()

        # Fallback: si cliente envió el autos_id en lugar del id_registro,
        # eliminamos el registro más reciente para ese autos_id + usuario
        if not registro:
            registro = VehiculoRegistrado.query.filter_by(autos_id=id, user_id=user_id)\
                .order_by(VehiculoRegistrado.created_at.desc()).first()
            if registro:
                print(f"delete_vehiculo fallback found registro.id={registro.id} for autos_id={id}")

        if not registro:
            return jsonify({"error": "Vehículo no encontrado"}), 404

        db.session.delete(registro)
        db.session.commit()
        return jsonify({"message": "Eliminado con éxito"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"delete_vehiculo error: {e}")
        return jsonify({"error": str(e)}), 500

# --- RUTAS PARA EL PERFIL ---

@vehiculos_bp.route("/vehiculos/brands", methods=["GET"])
def get_brands():
    brands = db.session.query(Auto.marca).distinct().all()
    return jsonify([b[0] for b in brands])

@vehiculos_bp.route("/vehiculos/models/<brand>", methods=["GET"])
def get_models(brand):
    autos = Auto.query.filter_by(marca=brand).all()
    return jsonify([{"id": a.id, "modelo": a.modelo, "anio": a.anio} for a in autos])

@vehiculos_bp.route("/vehiculos/assign", methods=["POST"])
def assign_vehicle():
    user_id = session.get("user_id")
    if not user_id: return jsonify({"error": "No auth"}), 401
    
    data = request.get_json()
    nuevo = VehiculoRegistrado(user_id=user_id, autos_id=data.get("autos_id"), created_at=datetime.utcnow())
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"message": "Ok"})

@vehiculos_bp.route("/vehiculos/current", methods=["GET"])
def get_current():
    user_id = session.get("user_id")
    if not user_id: return jsonify(None)
    reg = VehiculoRegistrado.query.filter_by(user_id=user_id).order_by(VehiculoRegistrado.created_at.desc()).first()
    if reg and reg.auto:
        return jsonify({"marca": reg.auto.marca, "modelo": reg.auto.modelo, "anio": reg.auto.anio})
    return jsonify(None)

@vehiculos_bp.route("/mis-vehiculos/", methods=["POST"])
def create_mi_vehiculo():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "No autenticado"}), 401

    # Intentar JSON silencioso, luego form-data y query params
    data = request.get_json(silent=True) or {}
    if not data:
        data = {}
        data.update(request.form.to_dict())
        data.update(request.args.to_dict())

    # Aceptar varios nombres comunes
    autos_id = data.get("autos_id") or data.get("id") or data.get("auto_id") or data.get("autosId")
    if not autos_id:
        return jsonify({"error": "Falta autos_id"}), 400

    try:
        autos_id = int(autos_id)
    except (TypeError, ValueError):
        return jsonify({"error": "autos_id inválido"}), 400

    auto = Auto.query.get(autos_id)
    if not auto:
        return jsonify({"error": "Auto no encontrado"}), 404

    try:
        nuevo = VehiculoRegistrado(user_id=user_id, autos_id=autos_id, created_at=datetime.utcnow())
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"message": "Ok", "id_registro": nuevo.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500