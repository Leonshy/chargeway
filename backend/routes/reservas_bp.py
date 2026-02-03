from flask import Blueprint, jsonify, request, session
from db import db
from datetime import datetime

from models.reserva import Reserva
from models.user import User

import random
import string

# funcion para generar código único de reserva
def generar_codigo_reserva(longitud=8):
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choices(caracteres, k=longitud))


reservas_bp = Blueprint("reservas_bp", __name__, url_prefix="/api/reservas")


@reservas_bp.route("/", methods=["GET"])
def obtener_reservas():
    """Obtener todas las reservas del usuario actual"""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        reservas = (
            Reserva.query
            .filter_by(user_id=session["user_id"])
            .order_by(Reserva.fecha.desc())
            .all()
        )
        return jsonify([r.to_dict() for r in reservas])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reservas_bp.route("/", methods=["POST"])
def crear_reserva():
    """Crear una nueva reserva (sin romper contrato con frontend)"""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    # Validar que el usuario exista realmente en la base de datos
    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"error": "Usuario inválido"}), 400

    try:
        data = request.get_json()

        # Validar datos requeridos (SE MANTIENE)
        required_fields = ["estacion_id", "fecha", "hora_inicio", "duracion"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Falta el campo: {field}"}), 400

        # Convertir fecha y hora (SE MANTIENE)
        fecha = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
        hora_inicio = datetime.strptime(data["hora_inicio"], "%H:%M").time()

        # generar código único 
        codigo_reserva = generar_codigo_reserva()

        # Crear reserva (SE MANTIENE + código)
        reserva = Reserva(
            user_id=session["user_id"],
            estacion_id=data["estacion_id"],
            estacion_nombre=data.get("estacion_nombre", ""),
            estacion_direccion=data.get("estacion_direccion", ""),
            fecha=fecha,
            hora_inicio=hora_inicio,
            duracion_horas=float(data["duracion"]),
            estado="activa",
            codigo=codigo_reserva,   # 👈 nuevo campo
        )

        db.session.add(reserva)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Reserva creada exitosamente",
                    "reserva": reserva.to_dict(),  # incluye el código
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": f"Formato de fecha/hora inválido: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@reservas_bp.route("/<int:reserva_id>", methods=["GET"])
def obtener_reserva(reserva_id):
    """Obtener una reserva específica"""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        reserva = Reserva.query.filter_by(
            id=reserva_id,
            user_id=session["user_id"]
        ).first()

        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        return jsonify(reserva.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reservas_bp.route("/<int:reserva_id>", methods=["DELETE"])
def cancelar_reserva(reserva_id):
    """Cancelar una reserva"""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        reserva = Reserva.query.filter_by(
            id=reserva_id,
            user_id=session["user_id"]
        ).first()

        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        reserva.estado = "cancelada"
        db.session.commit()

        return jsonify(
            {
                "message": "Reserva cancelada exitosamente",
                "reserva": reserva.to_dict(),
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@reservas_bp.route("/<int:reserva_id>", methods=["PUT"])
def actualizar_reserva(reserva_id):
    """Actualizar una reserva existente"""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        reserva = Reserva.query.filter_by(
            id=reserva_id,
            user_id=session["user_id"]
        ).first()

        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        data = request.get_json()

        if "fecha" in data:
            reserva.fecha = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
        if "hora_inicio" in data:
            reserva.hora_inicio = datetime.strptime(data["hora_inicio"], "%H:%M").time()
        if "duracion" in data:
            reserva.duracion_horas = float(data["duracion"])
        if "estado" in data:
            reserva.estado = data["estado"]

        db.session.commit()

        return jsonify(
            {
                "message": "Reserva actualizada exitosamente",
                "reserva": reserva.to_dict(),
            }
        )
    except ValueError as e:
        return jsonify({"error": f"Formato de fecha/hora inválido: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500