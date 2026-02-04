from flask import Blueprint, jsonify, request, session, current_app
from db import db
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

from models.reserva import Reserva
from models.user import User
from models.conectores import Connector
from models.estaciones import Station

# ✅ Usamos la factory que lee .env
from services.email_service import email_service_from_env

import random
import string


# ============================================
# 🔐 Función para generar código único de reserva
# ============================================
def generar_codigo_reserva(longitud=8):
    """Genera un código alfanumérico único para la reserva."""
    caracteres = string.ascii_uppercase + string.digits
    return "".join(random.choices(caracteres, k=longitud))


def get_email_service():
    """Helper para obtener el servicio de email configurado."""
    return email_service_from_env()


# ============================================
# 🔒 FUNCIÓN: VERIFICAR DISPONIBILIDAD POR CONECTOR
# ============================================
def verificar_disponibilidad_conector(
    conector_id, fecha, hora_inicio, duracion_horas, reserva_id_excluir=None
):
    """
    Verifica si un conector específico está disponible en el horario solicitado.

    Args:
        conector_id: ID del conector
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

    # Buscar reservas en el MISMO CONECTOR y fecha que NO estén canceladas
    query = Reserva.query.filter(
        and_(
            Reserva.conector_id == conector_id,
            Reserva.estado.in_(
                ["activa", "en_progreso", "completada"]
            ),  # Ignorar canceladas
            Reserva.fecha == fecha,  # Mismo día
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

        # Solapamiento existe si:
        # - La nueva reserva empieza antes de que termine la existente Y
        # - La nueva reserva termina después de que empiece la existente
        if fecha_hora_inicio < reserva_fin and fecha_hora_fin > reserva_inicio:
            reservas_conflictivas.append(
                {
                    "id": reserva.id,
                    "codigo": reserva.codigo,
                    "conector_id": reserva.conector_id,
                    "fecha": reserva.fecha.strftime("%Y-%m-%d"),
                    "hora_inicio": reserva.hora_inicio.strftime("%H:%M"),
                    "hora_fin": reserva_fin.strftime("%H:%M"),
                    "duracion_horas": reserva.duracion_horas,
                    "usuario": reserva.user.username if reserva.user else "Desconocido",
                }
            )

    disponible = len(reservas_conflictivas) == 0
    return disponible, reservas_conflictivas


def obtener_conectores_disponibles(estacion_id, fecha, hora_inicio, duracion_horas):
    """
    Obtiene los conectores disponibles de una estación para un horario específico.

    Args:
        estacion_id: ID de la estación
        fecha: Fecha de la reserva (date object)
        hora_inicio: Hora de inicio (time object)
        duracion_horas: Duración en horas (float)

    Returns:
        list: Lista de conectores disponibles con su información
    """
    # Obtener todos los conectores activos de la estación
    conectores = Connector.query.filter_by(estacion_id=estacion_id, activo=True).all()

    conectores_disponibles = []

    for conector in conectores:
        disponible, _ = verificar_disponibilidad_conector(
            conector.id, fecha, hora_inicio, duracion_horas
        )

        if disponible:
            conectores_disponibles.append(
                {
                    "id": conector.id,
                    "nombre": conector.nombre,
                    "tipo": conector.tipo,
                    "potencia_kw": conector.potencia_kw,
                    "disponible": True,
                }
            )

    return conectores_disponibles


reservas_bp = Blueprint("reservas_bp", __name__, url_prefix="/api/reservas")


# ============================================
# 🧪 Endpoint de prueba rápida (debug/hackatón)
# ============================================
@reservas_bp.route("/test-email", methods=["GET"])
def test_email():
    """Envía un email de confirmación usando la última reserva."""
    try:
        email_service = get_email_service()

        # Tomamos la última reserva
        reserva = Reserva.query.order_by(Reserva.id.desc()).first()
        if not reserva:
            return jsonify({"ok": False, "msg": "No hay reservas en la BD"}), 400

        # Tomamos el usuario dueño de la reserva
        user = User.query.get(reserva.user_id)
        if not user:
            return (
                jsonify(
                    {"ok": False, "msg": "No se encontró el usuario de la reserva"}
                ),
                400,
            )

        ok, msg, codigo = email_service.enviar_confirmacion_reserva(
            destinatario_email=user.email,
            destinatario_nombre=user.username,
            reserva=reserva,
        )

        return (
            jsonify(
                {"ok": ok, "msg": msg, "codigo": codigo, "destinatario": user.email}
            ),
            200 if ok else 500,
        )

    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


@reservas_bp.route("/", methods=["GET"])
def obtener_reservas():
    """Obtener todas las reservas del usuario actual con info del conector."""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        reservas = (
            Reserva.query.filter_by(user_id=session["user_id"])
            .order_by(Reserva.fecha.desc())
            .all()
        )
        # Incluimos info del conector en cada reserva
        return jsonify([r.to_dict(include_conector_info=True) for r in reservas])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reservas_bp.route("/", methods=["POST"])
def crear_reserva():
    """
    Crear una nueva reserva por conector y enviar email de confirmación.

    Body JSON:
    {
        "conector_id": int,  # REQUERIDO: ID del conector
        "fecha": "YYYY-MM-DD",
        "hora_inicio": "HH:MM",
        "duracion": float
    }
    """
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    # Validar que el usuario exista
    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"error": "Usuario inválido"}), 400

    try:
        data = request.get_json()

        # ✅ NUEVO: Validar que venga conector_id
        required_fields = ["conector_id", "fecha", "hora_inicio", "duracion"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Falta el campo: {field}"}), 400

        conector_id = int(data["conector_id"])

        # Verificar que el conector exista y esté activo
        conector = Connector.query.get(conector_id)
        if not conector:
            return jsonify({"error": "Conector no encontrado"}), 404

        if not conector.activo:
            return jsonify({"error": "Este conector no está disponible"}), 400

        # Obtener información de la estación
        estacion = Station.query.get(conector.estacion_id)
        if not estacion:
            return jsonify({"error": "Estación no encontrada"}), 404

        # Convertir fecha y hora
        fecha = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
        hora_inicio = datetime.strptime(data["hora_inicio"], "%H:%M").time()
        duracion = float(data["duracion"])

        # Validar duración mínima y máxima
        if duracion < 0.5:
            return (
                jsonify({"error": "La duración mínima es 0.5 horas (30 minutos)"}),
                400,
            )
        if duracion > 8:
            return jsonify({"error": "La duración máxima es 8 horas"}), 400

        # ✅ Validar que la fecha y hora sean futuras
        ahora = datetime.now()
        fecha_hora_reserva = datetime.combine(fecha, hora_inicio)

        if fecha_hora_reserva <= ahora:
            return (
                jsonify(
                    {
                        "error": "No se puede reservar en una fecha y hora pasada. Por favor selecciona una fecha y hora futura."
                    }
                ),
                400,
            )

        # 🔒 Verificar disponibilidad del CONECTOR específico
        disponible, conflictos = verificar_disponibilidad_conector(
            conector_id=conector_id,
            fecha=fecha,
            hora_inicio=hora_inicio,
            duracion_horas=duracion,
        )

        if not disponible:
            return (
                jsonify(
                    {
                        "error": "Conector no disponible",
                        "message": f"El conector {conector.nombre} ya tiene una reserva en ese horario",
                        "conflictos": conflictos,
                    }
                ),
                409,
            )

        # Generar código único de reserva
        codigo = generar_codigo_reserva()
        while Reserva.query.filter_by(codigo=codigo).first():
            codigo = generar_codigo_reserva()

        # ✅ Crear la reserva con conector_id
        nueva_reserva = Reserva(
            user_id=session["user_id"],
            conector_id=conector_id,
            estacion_id=conector.estacion_id,  # Se llena automáticamente desde el conector
            estacion_nombre=estacion.nombre,
            estacion_direccion=estacion.direccion,
            fecha=fecha,
            hora_inicio=hora_inicio,
            duracion_horas=duracion,
            estado="activa",
            codigo=codigo,
        )

        db.session.add(nueva_reserva)
        db.session.commit()

        # 📧 Enviar email de confirmación (si está habilitado)
        if current_app.config.get("EMAIL_ENABLED", True):
            try:
                email_service = get_email_service()
                email_service.enviar_confirmacion_reserva(
                    destinatario_email=user.email,
                    destinatario_nombre=user.username,
                    reserva=nueva_reserva,
                )
                print(f"✅ Email de confirmación enviado a {user.email}")
            except Exception as e:
                print(f"⚠️ Error al enviar email: {e}")

        return (
            jsonify(
                {
                    "message": "Reserva creada exitosamente",
                    "reserva": nueva_reserva.to_dict(include_conector_info=True),
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
    """Obtener una reserva específica con info del conector."""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        reserva = Reserva.query.filter_by(
            id=reserva_id, user_id=session["user_id"]
        ).first()
        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        return jsonify(reserva.to_dict(include_conector_info=True))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reservas_bp.route("/<int:reserva_id>", methods=["DELETE"])
def cancelar_reserva(reserva_id):
    """Cancelar una reserva y enviar email de confirmación."""
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        reserva = Reserva.query.filter_by(
            id=reserva_id, user_id=session["user_id"]
        ).first()
        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        user = User.query.get(session["user_id"])

        codigo_reserva = reserva.codigo
        reserva_data = {
            "estacion_nombre": reserva.estacion_nombre,
            "conector_nombre": reserva.conector.nombre if reserva.conector else "N/A",
            "fecha": reserva.fecha.strftime("%d/%m/%Y"),
            "hora_inicio": reserva.hora_inicio.strftime("%H:%M"),
        }

        reserva.estado = "cancelada"
        db.session.commit()

        # 📧 Enviar email de cancelación (si está habilitado)
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
                "reserva": reserva.to_dict(include_conector_info=True),
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@reservas_bp.route("/<int:reserva_id>", methods=["PUT"])
def actualizar_reserva(reserva_id):
    """
    Actualizar una reserva existente con validación de disponibilidad por conector.
    Permite cambiar el conector si se desea.
    """
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    try:
        reserva = Reserva.query.filter_by(
            id=reserva_id, user_id=session["user_id"]
        ).first()
        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        data = request.get_json()

        # Obtener nuevos valores o mantener los actuales
        nuevo_conector_id = int(data.get("conector_id", reserva.conector_id))
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

        # Si se cambia el conector, verificar que exista y esté activo
        if nuevo_conector_id != reserva.conector_id:
            nuevo_conector = Connector.query.get(nuevo_conector_id)
            if not nuevo_conector:
                return jsonify({"error": "Conector no encontrado"}), 404
            if not nuevo_conector.activo:
                return (
                    jsonify({"error": "El conector seleccionado no está disponible"}),
                    400,
                )

        # ✅ Validar fecha/hora futuras si se actualizan
        if "fecha" in data or "hora_inicio" in data:
            ahora = datetime.now()
            fecha_hora_nueva = datetime.combine(nueva_fecha, nueva_hora)
            if fecha_hora_nueva <= ahora:
                return (
                    jsonify(
                        {
                            "error": "No se puede actualizar a una fecha y hora pasada. Por favor selecciona una fecha y hora futura."
                        }
                    ),
                    400,
                )

        # 🔒 Validar disponibilidad si se cambia algo relevante
        if (
            "conector_id" in data
            or "fecha" in data
            or "hora_inicio" in data
            or "duracion" in data
        ):
            disponible, conflictos = verificar_disponibilidad_conector(
                conector_id=nuevo_conector_id,
                fecha=nueva_fecha,
                hora_inicio=nueva_hora,
                duracion_horas=nueva_duracion,
                reserva_id_excluir=reserva_id,
            )

            if not disponible:
                return (
                    jsonify(
                        {
                            "error": "Conector no disponible",
                            "message": "El horario seleccionado se solapa con otra reserva",
                            "conflictos": conflictos,
                        }
                    ),
                    409,
                )

        # Actualizar campos
        if "conector_id" in data:
            conector = Connector.query.get(nuevo_conector_id)
            estacion = Station.query.get(conector.estacion_id)
            reserva.conector_id = nuevo_conector_id
            reserva.estacion_id = conector.estacion_id
            reserva.estacion_nombre = (
                estacion.nombre if estacion else reserva.estacion_nombre
            )
            reserva.estacion_direccion = (
                estacion.direccion if estacion else reserva.estacion_direccion
            )

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
                "reserva": reserva.to_dict(include_conector_info=True),
            }
        )

    except ValueError as e:
        return jsonify({"error": f"Formato de fecha/hora inválido: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@reservas_bp.route("/<int:reserva_id>/reenviar-email", methods=["POST"])
def reenviar_email_confirmacion(reserva_id):
    """Reenviar email de confirmación de una reserva existente."""
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

        if current_app.config.get("EMAIL_ENABLED", True):
            email_service = get_email_service()

            success, mensaje, _ = email_service.enviar_confirmacion_reserva(
                destinatario_email=user.email,
                destinatario_nombre=user.username,
                reserva=reserva,
            )

            if success:
                return jsonify(
                    {"message": "Email reenviado exitosamente", "email": user.email}
                )
            return jsonify({"error": mensaje}), 500

        return jsonify({"error": "Envío de emails deshabilitado"}), 503

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# 🆕 ENDPOINT: VER CONECTORES DISPONIBLES DE UNA ESTACIÓN
# ============================================
@reservas_bp.route(
    "/estacion/<int:estacion_id>/conectores-disponibles", methods=["GET"]
)
def obtener_conectores_disponibles_estacion(estacion_id):
    """
    Obtener conectores disponibles de una estación para un horario específico.

    Query params:
    - fecha: YYYY-MM-DD (requerido)
    - hora_inicio: HH:MM (requerido)
    - duracion: float en horas (requerido)

    Ejemplo: /api/reservas/estacion/1/conectores-disponibles?fecha=2026-02-10&hora_inicio=14:00&duracion=2
    """
    try:
        # Validar parámetros requeridos
        fecha_str = request.args.get("fecha")
        hora_str = request.args.get("hora_inicio")
        duracion_str = request.args.get("duracion")

        if not all([fecha_str, hora_str, duracion_str]):
            return (
                jsonify(
                    {
                        "error": "Faltan parámetros",
                        "requeridos": ["fecha", "hora_inicio", "duracion"],
                    }
                ),
                400,
            )

        # Convertir parámetros
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        hora_inicio = datetime.strptime(hora_str, "%H:%M").time()
        duracion = float(duracion_str)

        # Obtener conectores disponibles
        conectores_disponibles = obtener_conectores_disponibles(
            estacion_id, fecha, hora_inicio, duracion
        )

        # Obtener todos los conectores de la estación para info completa
        todos_conectores = Connector.query.filter_by(
            estacion_id=estacion_id, activo=True
        ).all()

        return jsonify(
            {
                "estacion_id": estacion_id,
                "fecha": fecha_str,
                "hora_inicio": hora_str,
                "duracion_horas": duracion,
                "total_conectores": len(todos_conectores),
                "conectores_disponibles": len(conectores_disponibles),
                "conectores": conectores_disponibles,
            }
        )

    except ValueError as e:
        return jsonify({"error": f"Formato inválido: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# 🆕 ENDPOINT: VER RESERVAS POR CONECTOR
# ============================================
@reservas_bp.route("/conector/<int:conector_id>", methods=["GET"])
def obtener_reservas_conector(conector_id):
    """
    Obtener todas las reservas de un conector específico.

    Query params opcionales:
    - fecha: YYYY-MM-DD (opcional, filtra por fecha específica)
    """
    try:
        fecha_str = request.args.get("fecha")

        query = Reserva.query.filter(
            Reserva.conector_id == conector_id,
            Reserva.estado.in_(["activa", "en_progreso", "completada"]),
        )

        if fecha_str:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            query = query.filter(Reserva.fecha == fecha)

        reservas = query.order_by(Reserva.fecha, Reserva.hora_inicio).all()

        # Obtener info del conector
        conector = Connector.query.get(conector_id)

        return jsonify(
            {
                "conector_id": conector_id,
                "conector_nombre": conector.nombre if conector else "Desconocido",
                "total_reservas": len(reservas),
                "reservas": [r.to_dict() for r in reservas],
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# 🆕 ENDPOINT: VER RESERVAS POR ESTACIÓN (con info de conectores)
# ============================================
@reservas_bp.route("/estacion/<int:estacion_id>", methods=["GET"])
def obtener_reservas_estacion(estacion_id):
    """
    Obtener todas las reservas activas de una estación específica.
    Ahora muestra qué conector está usando cada reserva.
    """
    try:
        fecha_str = request.args.get("fecha")

        query = Reserva.query.filter(
            Reserva.estacion_id == estacion_id,
            Reserva.estado.in_(["activa", "en_progreso", "completada"]),
        )

        if fecha_str:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            query = query.filter(Reserva.fecha == fecha)

        reservas = query.order_by(Reserva.fecha, Reserva.hora_inicio).all()

        return jsonify(
            {
                "estacion_id": estacion_id,
                "total_reservas": len(reservas),
                "reservas": [r.to_dict(include_conector_info=True) for r in reservas],
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
