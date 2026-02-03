from flask import Blueprint, jsonify, request, session, current_app
from db import db
from datetime import datetime

from models.reserva import Reserva
from models.user import User
from services.email_service import EmailService

import random
import string

# Función para generar código único de reserva
def generar_codigo_reserva(longitud=8):
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choices(caracteres, k=longitud))


def get_email_service():
    """Helper para obtener el servicio de email configurado"""
    return EmailService(
        smtp_server=current_app.config['SMTP_SERVER'],
        smtp_port=current_app.config['SMTP_PORT'],
        email_user=current_app.config['EMAIL_USER'],
        email_password=current_app.config['EMAIL_PASSWORD']
    )


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
    """Crear una nueva reserva y enviar email de confirmación"""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    # Validar que el usuario exista realmente en la base de datos
    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"error": "Usuario inválido"}), 400

    try:
        data = request.get_json()

        # Validar datos requeridos
        required_fields = ["estacion_id", "fecha", "hora_inicio", "duracion"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Falta el campo: {field}"}), 400

        # Convertir fecha y hora
        fecha = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
        hora_inicio = datetime.strptime(data["hora_inicio"], "%H:%M").time()

        # Generar código único
        codigo_reserva = generar_codigo_reserva()

        # Crear reserva
        reserva = Reserva(
            user_id=session["user_id"],
            estacion_id=data["estacion_id"],
            estacion_nombre=data.get("estacion_nombre", ""),
            estacion_direccion=data.get("estacion_direccion", ""),
            fecha=fecha,
            hora_inicio=hora_inicio,
            duracion_horas=float(data["duracion"]),
            estado="activa",
            codigo=codigo_reserva,
        )

        db.session.add(reserva)
        db.session.flush()  # Flush para obtener el ID

        # ============================================
        # 📧 ENVIAR EMAIL DE CONFIRMACIÓN
        # ============================================
        email_enviado = False
        email_error = None

        if current_app.config.get('EMAIL_ENABLED', True):
            try:
                email_service = get_email_service()
                
                # Crear objeto mock con la estructura que espera el servicio de email
                class ReservaParaEmail:
                    def __init__(self, reserva_obj):
                        self.id = reserva_obj.id
                        self.estacion_nombre = reserva_obj.estacion_nombre
                        self.estacion_direccion = reserva_obj.estacion_direccion
                        self.fecha = reserva_obj.fecha
                        self.hora_inicio = reserva_obj.hora_inicio
                        self.duracion_horas = reserva_obj.duracion_horas
                
                reserva_email = ReservaParaEmail(reserva)
                
                # Enviar email (pero usamos tu código en lugar del generado por el servicio)
                success, mensaje, _ = email_service.enviar_confirmacion_reserva(
                    destinatario_email=user.email,
                    destinatario_nombre=user.username,
                    reserva=reserva_email
                )
                
                if success:
                    email_enviado = True
                    print(f"✅ Email enviado a {user.email} - Código: {codigo_reserva}")
                else:
                    email_error = mensaje
                    print(f"⚠️ Error al enviar email: {mensaje}")
                    
            except Exception as e:
                email_error = str(e)
                print(f"❌ Excepción al enviar email: {e}")
        else:
            print("📧 Envío de emails deshabilitado en configuración")

        # Hacer commit de la reserva
        db.session.commit()

        # Preparar respuesta
        response_data = {
            "message": "Reserva creada exitosamente",
            "reserva": reserva.to_dict(),
            "email_enviado": email_enviado
        }

        # Si hubo error en el email, informar pero no fallar
        if email_error:
            response_data["email_warning"] = f"Reserva creada pero no se pudo enviar el email: {email_error}"

        return jsonify(response_data), 201

    except ValueError as e:
        db.session.rollback()
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
    """Cancelar una reserva y enviar email de confirmación"""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        reserva = Reserva.query.filter_by(
            id=reserva_id,
            user_id=session["user_id"]
        ).first()

        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        # Obtener usuario para enviar email
        user = User.query.get(session["user_id"])
        
        # Guardar datos antes de cambiar estado
        codigo_reserva = reserva.codigo
        reserva_data = {
            'estacion_nombre': reserva.estacion_nombre,
            'fecha': reserva.fecha.strftime('%d/%m/%Y'),
            'hora_inicio': reserva.hora_inicio.strftime('%H:%M')
        }

        # Cambiar estado
        reserva.estado = "cancelada"
        db.session.commit()

        # 📧 Enviar email de cancelación
        if current_app.config.get('EMAIL_ENABLED', True) and user:
            try:
                email_service = get_email_service()
                email_service.enviar_cancelacion_reserva(
                    destinatario_email=user.email,
                    destinatario_nombre=user.username,
                    codigo_reserva=codigo_reserva,
                    reserva_data=reserva_data
                )
                print(f"✅ Email de cancelación enviado a {user.email}")
            except Exception as e:
                print(f"⚠️ Error al enviar email de cancelación: {e}")

        return jsonify({
            "message": "Reserva cancelada exitosamente",
            "reserva": reserva.to_dict(),
        })
        
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

        return jsonify({
            "message": "Reserva actualizada exitosamente",
            "reserva": reserva.to_dict(),
        })
        
    except ValueError as e:
        return jsonify({"error": f"Formato de fecha/hora inválido: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@reservas_bp.route("/<int:reserva_id>/reenviar-email", methods=["POST"])
def reenviar_email_confirmacion(reserva_id):
    """
    Reenviar email de confirmación de una reserva existente
    Útil si el usuario no recibió el email original
    """
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        reserva = Reserva.query.filter_by(
            id=reserva_id,
            user_id=session["user_id"]
        ).first()

        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        if reserva.estado != "activa":
            return jsonify({"error": "Solo se pueden reenviar emails de reservas activas"}), 400

        user = User.query.get(session["user_id"])
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Reenviar email
        if current_app.config.get('EMAIL_ENABLED', True):
            email_service = get_email_service()
            
            # Crear objeto para email
            class ReservaParaEmail:
                def __init__(self, reserva_obj):
                    self.id = reserva_obj.id
                    self.estacion_nombre = reserva_obj.estacion_nombre
                    self.estacion_direccion = reserva_obj.estacion_direccion
                    self.fecha = reserva_obj.fecha
                    self.hora_inicio = reserva_obj.hora_inicio
                    self.duracion_horas = reserva_obj.duracion_horas
            
            reserva_email = ReservaParaEmail(reserva)
            
            success, mensaje, _ = email_service.enviar_confirmacion_reserva(
                destinatario_email=user.email,
                destinatario_nombre=user.username,
                reserva=reserva_email
            )

            if success:
                return jsonify({
                    "message": "Email reenviado exitosamente",
                    "email": user.email
                })
            else:
                return jsonify({"error": mensaje}), 500
        else:
            return jsonify({"error": "Envío de emails deshabilitado"}), 503

    except Exception as e:
        return jsonify({"error": str(e)}), 500