from flask import Blueprint, jsonify, request, session, current_app
from db import db
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

from models.reserva import Reserva
from models.user import User
from services.email_service import EmailService

import random
import string


# Función para generar código único de reserva
def generar_codigo_reserva(longitud=8):
    caracteres = string.ascii_uppercase + string.digits
    return "".join(random.choices(caracteres, k=longitud))


def get_email_service():
    """Helper para obtener el servicio de email configurado"""
    return EmailService(
        smtp_server=current_app.config["SMTP_SERVER"],
        smtp_port=current_app.config["SMTP_PORT"],
        email_user=current_app.config["EMAIL_USER"],
        email_password=current_app.config["EMAIL_PASSWORD"],
    )


# ============================================
# 🔒 NUEVA FUNCIÓN: VERIFICAR DISPONIBILIDAD
# ============================================
def verificar_disponibilidad_estacion(
    estacion_id, fecha, hora_inicio, duracion_horas, reserva_id_excluir=None
):
    """
    Verifica si la estación está disponible en el horario solicitado.

    Args:
        estacion_id: ID de la estación
        fecha: Fecha de la reserva (date object)
        hora_inicio: Hora de inicio (time object)
        duracion_horas: Duración en horas (float)
        reserva_id_excluir: ID de reserva a excluir (útil para actualizaciones)

    Returns:
        tuple: (disponible: bool, reservas_conflictivas: list)
    """
    # Convertir hora_inicio a datetime para hacer cálculos
    fecha_hora_inicio = datetime.combine(fecha, hora_inicio)
    fecha_hora_fin = fecha_hora_inicio + timedelta(hours=duracion_horas)

    # Extraer solo la hora de fin para comparación
    hora_fin = fecha_hora_fin.time()
    fecha_fin = fecha_hora_fin.date()

    # Buscar reservas en la misma estación y fecha que NO estén canceladas
    query = Reserva.query.filter(
        and_(
            Reserva.estacion_id == estacion_id,
            Reserva.estado.in_(["activa", "completada"]),  # Ignorar canceladas
            or_(
                # Caso 1: Reservas que terminan después de la misma fecha
                Reserva.fecha == fecha,
                # Caso 2: Reservas que cruzan la medianoche
                and_(
                    Reserva.fecha < fecha,
                    Reserva.fecha
                    >= fecha,  # Verificar día siguiente si cruza medianoche
                ),
            ),
        )
    )

    # Si estamos actualizando una reserva, excluirla de la búsqueda
    if reserva_id_excluir:
        query = query.filter(Reserva.id != reserva_id_excluir)

    reservas_existentes = query.all()

    # Verificar solapamientos
    reservas_conflictivas = []

    for reserva in reservas_existentes:
        # Calcular hora de fin de la reserva existente
        reserva_inicio = datetime.combine(reserva.fecha, reserva.hora_inicio)
        reserva_fin = reserva_inicio + timedelta(hours=reserva.duracion_horas)

        # Verificar si hay solapamiento
        # Solapamiento existe si:
        # - La nueva reserva empieza antes de que termine la existente Y
        # - La nueva reserva termina después de que empiece la existente
        if fecha_hora_inicio < reserva_fin and fecha_hora_fin > reserva_inicio:
            reservas_conflictivas.append(
                {
                    "id": reserva.id,
                    "codigo": reserva.codigo,
                    "fecha": reserva.fecha.strftime("%Y-%m-%d"),
                    "hora_inicio": reserva.hora_inicio.strftime("%H:%M"),
                    "hora_fin": reserva_fin.strftime("%H:%M"),
                    "duracion_horas": reserva.duracion_horas,
                    "usuario": reserva.user.username if reserva.user else "Desconocido",
                }
            )

    disponible = len(reservas_conflictivas) == 0
    return disponible, reservas_conflictivas


reservas_bp = Blueprint("reservas_bp", __name__, url_prefix="/api/reservas")


@reservas_bp.route("/", methods=["GET"])
def obtener_reservas():
    """Obtener todas las reservas del usuario actual"""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        reservas = (
            Reserva.query.filter_by(user_id=session["user_id"])
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
        duracion = float(data["duracion"])

        # ============================================
        # ✅ VALIDAR QUE LA FECHA Y HORA SEAN FUTURAS
        # ============================================
        ahora = datetime.now()
        fecha_hora_reserva = datetime.combine(fecha, hora_inicio)
        
        if fecha_hora_reserva <= ahora:
            return jsonify({
                "error": "No se puede reservar en una fecha y hora pasada. Por favor selecciona una fecha y hora futura."
            }), 400

        # ============================================
        # ✅ VALIDAR QUE NO TENGA NINGUNA RESERVA ACTIVA
        # ============================================
        # Buscar cualquier reserva activa del usuario
        reservas_activas = Reserva.query.filter_by(
            user_id=session["user_id"],
            estado="activa"
        ).all()
        
        # Si tiene alguna reserva activa, verificar si ya terminó
        for reserva_activa in reservas_activas:
            # Calcular el fin de la reserva activa
            fecha_hora_inicio = datetime.combine(reserva_activa.fecha, reserva_activa.hora_inicio)
            fecha_hora_fin = fecha_hora_inicio + timedelta(hours=reserva_activa.duracion_horas)
            
            # Si la reserva activa aún no ha terminado (está en curso o es futura)
            if fecha_hora_fin > ahora:
                return jsonify({
                    "error": f"Ya tienes una reserva activa. Finaliza a las {fecha_hora_fin.strftime('%H:%M del %d/%m/%Y')}. No puedes hacer otra reserva hasta que termine.",
                    "reserva_activa": {
                        "estacion": reserva_activa.estacion_nombre,
                        "fecha": reserva_activa.fecha.strftime('%d/%m/%Y'),
                        "hora_inicio": reserva_activa.hora_inicio.strftime('%H:%M'),
                        "hora_fin": fecha_hora_fin.strftime('%H:%M'),
                        "duracion_horas": reserva_activa.duracion_horas,
                        "codigo": reserva_activa.codigo
                    }
                }), 400

        # ============================================
        # 🔒 VALIDAR DISPONIBILIDAD DE LA ESTACIÓN
        # ============================================
        disponible, conflictos = verificar_disponibilidad_estacion(
            estacion_id=data["estacion_id"],
            fecha=fecha,
            hora_inicio=hora_inicio,
            duracion_horas=duracion,
        )

        if not disponible:
            return (
                jsonify(
                    {
                        "error": "Estación no disponible",
                        "message": "Ya existe una reserva activa en el horario solicitado",
                        "conflictos": conflictos,
                    }
                ),
                409,
            )  # 409 Conflict

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
            duracion_horas=duracion,
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

        if current_app.config.get("EMAIL_ENABLED", True):
            try:
                email_service = get_email_service()

                # Crear objeto mock con la estructura que espera el servicio de email
                class ReservaParaEmail:
                    def __init__(self, reserva_obj):
                        self.id = reserva_obj.id
                        self.codigo = reserva_obj.codigo
                        self.estacion_nombre = reserva_obj.estacion_nombre
                        self.estacion_direccion = reserva_obj.estacion_direccion
                        self.fecha = reserva_obj.fecha
                        self.hora_inicio = reserva_obj.hora_inicio
                        self.duracion_horas = reserva_obj.duracion_horas

                reserva_email = ReservaParaEmail(reserva)

                # Enviar email
                success, mensaje, _ = email_service.enviar_confirmacion_reserva(
                    destinatario_email=user.email,
                    destinatario_nombre=user.username,
                    reserva=reserva_email,
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
            "email_enviado": email_enviado,
        }

        # Si hubo error en el email, informar pero no fallar
        if email_error:
            response_data["email_warning"] = (
                f"Reserva creada pero no se pudo enviar el email: {email_error}"
            )

        return jsonify(response_data), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": f"Formato de fecha/hora inválido: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ============================================
# 🆕 NUEVO ENDPOINT: VERIFICAR DISPONIBILIDAD
# ============================================
@reservas_bp.route("/verificar-disponibilidad", methods=["POST"])
def verificar_disponibilidad():
    """
    Endpoint para verificar disponibilidad sin crear la reserva.
    Útil para validación en tiempo real en el frontend.
    """
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
        duracion = float(data["duracion"])

        # Verificar disponibilidad
        disponible, conflictos = verificar_disponibilidad_estacion(
            estacion_id=data["estacion_id"],
            fecha=fecha,
            hora_inicio=hora_inicio,
            duracion_horas=duracion,
            reserva_id_excluir=data.get("reserva_id_excluir"),  # Para actualizar
        )

        return jsonify({"disponible": disponible, "conflictos": conflictos})

    except ValueError as e:
        return jsonify({"error": f"Formato de fecha/hora inválido: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reservas_bp.route("/<int:reserva_id>", methods=["GET"])
def obtener_reserva(reserva_id):
    """Obtener una reserva específica"""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        reserva = Reserva.query.filter_by(
            id=reserva_id, user_id=session["user_id"]
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
            id=reserva_id, user_id=session["user_id"]
        ).first()

        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        # Obtener usuario para enviar email
        user = User.query.get(session["user_id"])

        # Guardar datos antes de cambiar estado
        codigo_reserva = reserva.codigo
        reserva_data = {
            "estacion_nombre": reserva.estacion_nombre,
            "fecha": reserva.fecha.strftime("%d/%m/%Y"),
            "hora_inicio": reserva.hora_inicio.strftime("%H:%M"),
        }

        # Cambiar estado
        reserva.estado = "cancelada"
        db.session.commit()

        # 📧 Enviar email de cancelación
        if current_app.config.get("EMAIL_ENABLED", True) and user:
            try:
                email_service = get_email_service()
                email_service.enviar_cancelacion_reserva(
                    destinatario_email=user.email,
                    destinatario_nombre=user.username,
                    codigo_reserva=codigo_reserva,
                    reserva_data=reserva_data,
                )
                print(f"✅ Email de cancelación enviado a {user.email}")
            except Exception as e:
                print(f"⚠️ Error al enviar email de cancelación: {e}")

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
    """Actualizar una reserva existente con validación de disponibilidad"""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        reserva = Reserva.query.filter_by(
            id=reserva_id, user_id=session["user_id"]
        ).first()

        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        data = request.get_json()

        # Obtener valores actuales o nuevos
        nueva_fecha = (
            datetime.strptime(data["fecha"], "%Y-%m-%d").date()
            if "fecha" in data
            else reserva.fecha
        )
        nueva_hora = (
            datetime.strptime(data["hora_inicio"], "%H:%M").time()
            if "hora_inicio" in data
            else reserva.hora_inicio
        )
        nueva_duracion = (
            float(data["duracion"]) if "duracion" in data else reserva.duracion_horas
        )

        # ============================================
        # ✅ VALIDAR FECHA Y HORA SI SE ESTÁN ACTUALIZANDO
        # ============================================
        if "fecha" in data or "hora_inicio" in data:
            # Validar que sean futuras
            ahora = datetime.now()
            fecha_hora_nueva = datetime.combine(nueva_fecha, nueva_hora)
            
            if fecha_hora_nueva <= ahora:
                return jsonify({
                    "error": "No se puede actualizar a una fecha y hora pasada. Por favor selecciona una fecha y hora futura."
                }), 400

        # ============================================
        # 🔒 VALIDAR DISPONIBILIDAD SI SE CAMBIA HORARIO
        # ============================================
        if "fecha" in data or "hora_inicio" in data or "duracion" in data:
            disponible, conflictos = verificar_disponibilidad_estacion(
                estacion_id=reserva.estacion_id,
                fecha=nueva_fecha,
                hora_inicio=nueva_hora,
                duracion_horas=nueva_duracion,
                reserva_id_excluir=reserva_id,  # Excluir esta misma reserva
            )

            if not disponible:
                return (
                    jsonify(
                        {
                            "error": "Estación no disponible",
                            "message": "El nuevo horario se solapa con otra reserva",
                            "conflictos": conflictos,
                        }
                    ),
                    409,
                )

        # Actualizar campos
        if "fecha" in data:
            reserva.fecha = nueva_fecha
        if "hora_inicio" in data:
            reserva.hora_inicio = nueva_hora
        if "duracion" in data:
            reserva.duracion_horas = nueva_duracion
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
            id=reserva_id, user_id=session["user_id"]
        ).first()

        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        if reserva.estado != "activa":
            return (
                jsonify(
                    {"error": "Solo se pueden reenviar emails de reservas activas"}
                ),
                400,
            )

        user = User.query.get(session["user_id"])
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Reenviar email
        if current_app.config.get("EMAIL_ENABLED", True):
            email_service = get_email_service()

            # Crear objeto para email
            class ReservaParaEmail:
                def __init__(self, reserva_obj):
                    self.id = reserva_obj.id
                    self.codigo = reserva_obj.codigo
                    self.estacion_nombre = reserva_obj.estacion_nombre
                    self.estacion_direccion = reserva_obj.estacion_direccion
                    self.fecha = reserva_obj.fecha
                    self.hora_inicio = reserva_obj.hora_inicio
                    self.duracion_horas = reserva_obj.duracion_horas

            reserva_email = ReservaParaEmail(reserva)

            success, mensaje, _ = email_service.enviar_confirmacion_reserva(
                destinatario_email=user.email,
                destinatario_nombre=user.username,
                reserva=reserva_email,
            )

            if success:
                return jsonify(
                    {"message": "Email reenviado exitosamente", "email": user.email}
                )
            else:
                return jsonify({"error": mensaje}), 500
        else:
            return jsonify({"error": "Envío de emails deshabilitado"}), 503

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# 🆕 ENDPOINT ADICIONAL: VER RESERVAS POR ESTACIÓN
# ============================================
@reservas_bp.route("/estacion/<int:estacion_id>", methods=["GET"])
def obtener_reservas_estacion(estacion_id):
    """
    Obtener todas las reservas activas de una estación específica
    Útil para mostrar disponibilidad en el frontend
    """
    try:
        # Parámetros opcionales
        fecha_str = request.args.get("fecha")

        query = Reserva.query.filter(
            Reserva.estacion_id == estacion_id,
            Reserva.estado.in_(["activa", "completada"]),
        )

        # Filtrar por fecha si se proporciona
        if fecha_str:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            query = query.filter(Reserva.fecha == fecha)

        reservas = query.order_by(Reserva.fecha, Reserva.hora_inicio).all()

        return jsonify(
            {
                "estacion_id": estacion_id,
                "total_reservas": len(reservas),
                "reservas": [r.to_dict() for r in reservas],
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500