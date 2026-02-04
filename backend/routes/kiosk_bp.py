from flask import Blueprint, jsonify, request
from db import db
from datetime import datetime, timedelta, time
from models.reserva import Reserva
from models.conectores import Connector
from models.estaciones import Station

kiosk_bp = Blueprint("kiosk_bp", __name__, url_prefix="/api/kiosk")


# ============================================
# 🔌 ENDPOINT: VERIFICAR CÓDIGO DE RESERVA
# ============================================
@kiosk_bp.route("/verificar", methods=["POST"])
def verificar_codigo():
    """
    Verificar si un código de reserva es válido y puede ser activado.

    Validaciones:
    - El código existe
    - La reserva está en estado 'activa' o 'en_progreso'
    - La fecha/hora está dentro de la ventana permitida (±30 minutos)
    """
    try:
        data = request.get_json()
        codigo = data.get("codigo", "").strip().upper()

        if not codigo:
            return jsonify({"error": "Código de reserva requerido"}), 400

        # Buscar reserva por código
        reserva = Reserva.query.filter_by(codigo=codigo).first()

        if not reserva:
            return (
                jsonify(
                    {
                        "valid": False,
                        "error": "Código de reserva no encontrado",
                        "code": "NOT_FOUND",
                    }
                ),
                404,
            )

        # Verificar estado
        if reserva.estado not in ["activa", "en_progreso"]:
            return (
                jsonify(
                    {
                        "valid": False,
                        "error": f"Esta reserva está {reserva.estado}",
                        "code": "INVALID_STATE",
                        "estado": reserva.estado,
                    }
                ),
                400,
            )

        # Verificar ventana de tiempo (±30 minutos)
        ahora = datetime.now()
        fecha_hora_reserva = datetime.combine(reserva.fecha, reserva.hora_inicio)
        fecha_hora_fin = fecha_hora_reserva + timedelta(hours=reserva.duracion_horas)

        # Ventana de 30 minutos antes y durante toda la reserva
        ventana_inicio = fecha_hora_reserva - timedelta(minutes=30)
        ventana_fin = fecha_hora_fin

        if not (ventana_inicio <= ahora <= ventana_fin):
            # Calcular si es antes o después
            if ahora < ventana_inicio:
                diferencia = ventana_inicio - ahora
                minutos = int(diferencia.total_seconds() / 60)
                return (
                    jsonify(
                        {
                            "valid": False,
                            "error": f"Reserva programada para dentro de {minutos} minutos",
                            "code": "TOO_EARLY",
                            "minutos_restantes": minutos,
                        }
                    ),
                    400,
                )
            else:
                return (
                    jsonify(
                        {
                            "valid": False,
                            "error": "La reserva ya expiró",
                            "code": "EXPIRED",
                        }
                    ),
                    400,
                )

        # Obtener información de la estación
        estacion = Station.query.get(reserva.estacion_id)

        # Obtener conectores disponibles de la estación
        conectores = Connector.query.filter_by(
            estacion_id=reserva.estacion_id, activo=True
        ).all()

        # Preparar respuesta
        response_data = {
            "valid": True,
            "reserva": reserva.to_dict(include_user_info=True),
            "estacion": estacion.to_dict() if estacion else None,
            "conectores_disponibles": [c.to_dict() for c in conectores],
            "mensaje": "Código válido. Puede proceder a iniciar la carga.",
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# 🚀 ENDPOINT: INICIAR CARGA (Confirmar llegada)
# ============================================
@kiosk_bp.route("/iniciar-carga", methods=["POST"])
def iniciar_carga():
    """
    Confirmar llegada del usuario e iniciar el proceso de carga.

    Cambia estado de 'activa' → 'en_progreso'
    Registra hora_inicio_real
    Opcionalmente asigna un conector
    """
    try:
        data = request.get_json()
        codigo = data.get("codigo", "").strip().upper()
        conector_id = data.get("conector_id")  # Opcional

        if not codigo:
            return jsonify({"error": "Código de reserva requerido"}), 400

        # Buscar reserva
        reserva = Reserva.query.filter_by(codigo=codigo).first()

        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        # Validar estado
        if reserva.estado not in ["activa", "en_progreso"]:
            return (
                jsonify(
                    {"error": f"No se puede iniciar. Reserva está {reserva.estado}"}
                ),
                400,
            )

        # Si ya está en progreso, solo devolver info
        if reserva.estado == "en_progreso":
            return (
                jsonify(
                    {
                        "message": "La carga ya está en progreso",
                        "reserva": reserva.to_dict(include_user_info=True),
                    }
                ),
                200,
            )

        # Registrar inicio real
        reserva.estado = "en_progreso"
        reserva.hora_inicio_real = datetime.now()

        # Asignar conector si se proporciona
        if conector_id:
            conector = Connector.query.get(conector_id)
            if conector and conector.estacion_id == reserva.estacion_id:
                reserva.conector_id = conector_id

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Carga iniciada exitosamente",
                    "reserva": reserva.to_dict(include_user_info=True),
                    "hora_inicio_real": reserva.hora_inicio_real.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ============================================
# 🏁 ENDPOINT: FINALIZAR CARGA
# ============================================
@kiosk_bp.route("/finalizar-carga", methods=["POST"])
def finalizar_carga():
    """
    Finalizar el proceso de carga.

    Cambia estado de 'en_progreso' → 'completada'
    Registra hora_fin_real
    Calcula duracion_real_horas
    """
    try:
        data = request.get_json()
        codigo = data.get("codigo", "").strip().upper()

        if not codigo:
            return jsonify({"error": "Código de reserva requerido"}), 400

        # Buscar reserva
        reserva = Reserva.query.filter_by(codigo=codigo).first()

        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        # Validar que esté en progreso
        if reserva.estado != "en_progreso":
            return (
                jsonify(
                    {"error": f"No se puede finalizar. Reserva está {reserva.estado}"}
                ),
                400,
            )

        # Registrar finalización
        ahora = datetime.now()
        reserva.hora_fin_real = ahora
        reserva.estado = "completada"

        # Calcular duración real
        if reserva.hora_inicio_real:
            duracion_real = ahora - reserva.hora_inicio_real
            reserva.duracion_real_horas = round(duracion_real.total_seconds() / 3600, 2)

        db.session.commit()

        # Preparar resumen
        resumen = {
            "message": "Carga finalizada exitosamente",
            "reserva": reserva.to_dict(include_user_info=True),
            "resumen": {
                "hora_inicio_programada": datetime.combine(
                    reserva.fecha, reserva.hora_inicio
                ).strftime("%Y-%m-%d %H:%M"),
                "hora_inicio_real": reserva.hora_inicio_real.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "hora_fin_real": reserva.hora_fin_real.strftime("%Y-%m-%d %H:%M:%S"),
                "duracion_programada_horas": reserva.duracion_horas,
                "duracion_real_horas": reserva.duracion_real_horas,
                "diferencia_minutos": (
                    round(
                        (reserva.duracion_real_horas - reserva.duracion_horas) * 60, 1
                    )
                    if reserva.duracion_real_horas
                    else 0
                ),
            },
        }

        return jsonify(resumen), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ============================================
# 📊 ENDPOINT: CONSULTAR ESTADO
# ============================================
@kiosk_bp.route("/estado/<codigo>", methods=["GET"])
def consultar_estado(codigo):
    """
    Consultar el estado actual de una reserva por su código.
    Útil para polling en el frontend.
    """
    try:
        codigo = codigo.strip().upper()

        reserva = Reserva.query.filter_by(codigo=codigo).first()

        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        # Calcular tiempo restante si está en progreso
        tiempo_restante = None
        if reserva.estado == "en_progreso" and reserva.hora_inicio_real:
            tiempo_transcurrido = datetime.now() - reserva.hora_inicio_real
            horas_transcurridas = tiempo_transcurrido.total_seconds() / 3600
            horas_restantes = max(0, reserva.duracion_horas - horas_transcurridas)
            tiempo_restante = {
                "horas": int(horas_restantes),
                "minutos": int((horas_restantes % 1) * 60),
                "porcentaje_completado": min(
                    100, round((horas_transcurridas / reserva.duracion_horas) * 100, 1)
                ),
            }

        return (
            jsonify(
                {
                    "reserva": reserva.to_dict(include_user_info=True),
                    "tiempo_restante": tiempo_restante,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# 📋 ENDPOINT: LISTAR RESERVAS DE HOY EN UNA ESTACIÓN
# ============================================
@kiosk_bp.route("/estacion/<int:estacion_id>/hoy", methods=["GET"])
def reservas_hoy_estacion(estacion_id):
    """
    Listar todas las reservas del día actual para una estación específica.
    Útil para mostrar un dashboard en el kiosk.
    """
    try:
        hoy = datetime.now().date()

        reservas = (
            Reserva.query.filter(
                Reserva.estacion_id == estacion_id,
                Reserva.fecha == hoy,
                Reserva.estado.in_(["activa", "en_progreso", "completada"]),
            )
            .order_by(Reserva.hora_inicio)
            .all()
        )

        return (
            jsonify(
                {
                    "estacion_id": estacion_id,
                    "fecha": hoy.strftime("%Y-%m-%d"),
                    "total_reservas": len(reservas),
                    "reservas": [r.to_dict(include_user_info=False) for r in reservas],
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
