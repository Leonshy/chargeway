from flask import Blueprint, request, jsonify, session
from functools import wraps
from db import db
from sqlalchemy import text, inspect
import json
from datetime import datetime

# Importar todos los modelos
from models.user import User
from models.reserva import Reserva
from models.estaciones import Station
from models.vehiculo_registrado import VehiculoRegistrado
from models.vehiculos import Auto
from models.conectores import Connector

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/api/admin")


# ============================================
# 🔒 DECORADOR DE AUTENTICACIÓN ADMIN
# ============================================
def admin_required(f):
    """Decorador para proteger rutas que requieren permisos de admin"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar si el usuario está autenticado
        if "user_id" not in session:
            return jsonify({"error": "No autenticado", "code": "AUTH_REQUIRED"}), 401

        # Verificar si el usuario es admin
        user = User.query.get(session["user_id"])
        if not user:
            return (
                jsonify({"error": "Usuario no encontrado", "code": "USER_NOT_FOUND"}),
                404,
            )

        if not user.is_admin():
            return (
                jsonify(
                    {
                        "error": "Acceso denegado. Se requieren permisos de administrador.",
                        "code": "FORBIDDEN",
                    }
                ),
                403,
            )

        return f(*args, **kwargs)

    return decorated_function


# ============================================
# CONFIGURACIÓN DE MODELOS
# ============================================
MODELS_CONFIG = {
    "users": {
        "model": User,
        "name": "Usuarios",
        "icon": "👤",
        "fields": {
            "id": {"label": "ID", "type": "number", "readonly": True},
            "username": {"label": "Usuario", "type": "text", "required": True},
            "email": {"label": "Email", "type": "email", "required": True},
            "phone": {"label": "Teléfono", "type": "text"},
            "role": {
                "label": "Rol",
                "type": "select",
                "options": ["user", "admin"],
                "default": "user",
            },
            "is_active": {"label": "Activo", "type": "boolean", "default": True},
            "created_at": {
                "label": "Fecha Creación",
                "type": "datetime",
                "readonly": True,
            },
        },
    },
    "reservas": {
        "model": Reserva,
        "name": "Reservas",
        "icon": "📅",
        "fields": {
            "id": {"label": "ID", "type": "number", "readonly": True},
            "codigo": {"label": "Código", "type": "text", "readonly": True},
            "username": {"label": "Usuario", "type": "text", "readonly": True},  # 🆕 NUEVO
            "user_id": {"label": "ID Usuario", "type": "number", "required": True},
            "estacion_id": {"label": "ID Estación", "type": "number", "required": True},
            "estacion_nombre": {"label": "Estación", "type": "text"},
            "estacion_direccion": {"label": "Dirección", "type": "text"},
            "fecha": {"label": "Fecha", "type": "date", "required": True},
            "hora_inicio": {"label": "Hora Inicio", "type": "time", "required": True},
            "duracion_horas": {
                "label": "Duración (hrs)",
                "type": "number",
                "required": True,
            },
            "estado": {
                "label": "Estado",
                "type": "select",
                "options": ["activa", "completada", "cancelada"],
            },
            "created_at": {
                "label": "Fecha Creación",
                "type": "datetime",
                "readonly": True,
            },
        },
    },
    "stations": {
        "model": Station,
        "name": "Estaciones",
        "icon": "⚡",
        "fields": {
            "id": {"label": "ID", "type": "number", "readonly": True},
            "external_id": {"label": "ID Externo", "type": "number"},
            "nombre": {"label": "Nombre", "type": "text", "required": True},
            "direccion": {"label": "Dirección", "type": "text", "required": True},
            "ciudad": {"label": "Ciudad", "type": "text"},
            "pais": {"label": "País", "type": "text", "default": "Paraguay"},
            "lat": {"label": "Latitud", "type": "number", "required": True},
            "lng": {"label": "Longitud", "type": "number", "required": True},
            "operador": {"label": "Operador", "type": "text"},
            "activo": {"label": "Activo", "type": "boolean", "default": True},
            "created_at": {
                "label": "Fecha Creación",
                "type": "datetime",
                "readonly": True,
            },
        },
    },
    "autos": {
        "model": Auto,
        "name": "Vehículos EV",
        "icon": "🚗",
        "fields": {
            "id": {"label": "ID", "type": "number", "readonly": True},
            "marca": {"label": "Marca", "type": "text", "required": True},
            "modelo": {"label": "Modelo", "type": "text", "required": True},
            "anio": {"label": "Año", "type": "number", "required": True},
            "tipo": {"label": "Tipo", "type": "text"},
            "bateria_kwh": {"label": "Batería (kWh)", "type": "number"},
            "autonomia_km": {"label": "Autonomía (km)", "type": "number"},
            "potencia_hp": {"label": "Potencia (HP)", "type": "number"},
            "consumo_est_kwh_100km": {"label": "Consumo (kWh/100km)", "type": "number"},
            "puerto_de_carga": {"label": "Puerto de Carga", "type": "text"},
        },
    },
    "connectors": {
        "model": Connector,
        "name": "Conectores",
        "icon": "🔌",
        "fields": {
            "id": {"label": "ID", "type": "number", "readonly": True},
            "estacion_id": {"label": "ID Estación", "type": "number", "required": True},
            "nombre": {"label": "Nombre", "type": "text", "required": True},
            "tipo": {"label": "Tipo", "type": "text", "required": True},
            "potencia_kw": {
                "label": "Potencia (kW)",
                "type": "number",
                "required": True,
            },
            "activo": {"label": "Activo", "type": "boolean", "default": True},
            "created_at": {
                "label": "Fecha Creación",
                "type": "datetime",
                "readonly": True,
            },
        },
    },
    "vehiculos_registrados": {
        "model": VehiculoRegistrado,
        "name": "Vehículos Registrados",
        "icon": "📝",
        "fields": {
            "id": {"label": "ID", "type": "number", "readonly": True},
            "user_id": {"label": "ID Usuario", "type": "number", "required": True},
            "autos_id": {"label": "ID Auto", "type": "number", "required": True},
            "created_at": {
                "label": "Fecha Creación",
                "type": "datetime",
                "readonly": True,
            },
        },
    },
}


# ============================================
# 📊 ENDPOINTS PRINCIPALES
# ============================================


@admin_bp.route("/check-admin", methods=["GET"])
def check_admin():
    """Verificar si el usuario actual es admin"""
    if "user_id" not in session:
        return jsonify({"is_admin": False, "authenticated": False}), 200

    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"is_admin": False, "authenticated": False}), 200

    return jsonify(
        {
            "is_admin": user.is_admin(),
            "authenticated": True,
            "user": user.to_dict(include_role=True),
        }
    )


@admin_bp.route("/models", methods=["GET"])
@admin_required
def list_models():
    """Listar todos los modelos disponibles para administrar"""
    models_list = []

    for key, config in MODELS_CONFIG.items():
        try:
            count = config["model"].query.count()
        except:
            count = 0

        models_list.append(
            {
                "key": key,
                "name": config["name"],
                "icon": config["icon"],
                "count": count,
                "fields": config["fields"],
            }
        )

    return jsonify(models_list)


@admin_bp.route("/data/<model_name>", methods=["GET"])
@admin_required
def get_model_data(model_name):
    """Obtener todos los registros de un modelo"""
    if model_name not in MODELS_CONFIG:
        return jsonify({"error": "Modelo no encontrado"}), 404

    try:
        model = MODELS_CONFIG[model_name]["model"]

        # Parámetros de paginación
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)
        search = request.args.get("search", "", type=str)
        sort_by = request.args.get("sort_by", "id", type=str)
        sort_order = request.args.get("sort_order", "desc", type=str)

        # Query base
        query = model.query

        # 🆕 AGREGAR USERNAME PARA RESERVAS
        if model_name == "reservas":
            query = query.join(User, Reserva.user_id == User.id).add_columns(User.username)

        # Búsqueda (busca en campos de texto)
        if search:
            # Buscar en campos relevantes según el modelo
            search_filters = []
            if hasattr(model, "username"):
                search_filters.append(model.username.ilike(f"%{search}%"))
            if hasattr(model, "email"):
                search_filters.append(model.email.ilike(f"%{search}%"))
            if hasattr(model, "nombre"):
                search_filters.append(model.nombre.ilike(f"%{search}%"))
            if hasattr(model, "codigo"):
                search_filters.append(model.codigo.ilike(f"%{search}%"))
            if hasattr(model, "marca"):
                search_filters.append(model.marca.ilike(f"%{search}%"))
            if hasattr(model, "modelo"):
                search_filters.append(model.modelo.ilike(f"%{search}%"))
            
            # 🆕 Para reservas, buscar también por username
            if model_name == "reservas":
                search_filters.append(User.username.ilike(f"%{search}%"))

            if search_filters:
                from sqlalchemy import or_

                query = query.filter(or_(*search_filters))

        # Ordenamiento
        if hasattr(model, sort_by):
            column = getattr(model, sort_by)
            if sort_order == "asc":
                query = query.order_by(column.asc())
            else:
                query = query.order_by(column.desc())

        # Paginación
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # Convertir a diccionarios
        data = []
        for item in pagination.items:
            # 🆕 Si es reserva, viene como tupla (reserva, username)
            if model_name == "reservas":
                reserva_obj = item[0]
                username = item[1]
                
                if hasattr(reserva_obj, "to_dict"):
                    item_dict = reserva_obj.to_dict()
                else:
                    item_dict = {}
                    for column in inspect(reserva_obj.__class__).columns:
                        value = getattr(reserva_obj, column.name)
                        if isinstance(value, datetime):
                            value = value.strftime("%Y-%m-%d %H:%M:%S")
                        elif isinstance(value, (list, dict)):
                            value = str(value)
                        item_dict[column.name] = value
                
                # 🆕 AGREGAR USERNAME
                item_dict["username"] = username
                data.append(item_dict)
                
            # 🆕 Si es usuarios, asegurarse de incluir el role
            elif model_name == "users":
                if hasattr(item, "to_dict"):
                    item_dict = item.to_dict(include_role=True)
                else:
                    item_dict = {}
                    for column in inspect(item.__class__).columns:
                        value = getattr(item, column.name)
                        if isinstance(value, datetime):
                            value = value.strftime("%Y-%m-%d %H:%M:%S")
                        elif isinstance(value, (list, dict)):
                            value = str(value)
                        item_dict[column.name] = value
                data.append(item_dict)
                
            else:
                # Comportamiento normal para otros modelos
                if hasattr(item, "to_dict"):
                    data.append(item.to_dict())
                else:
                    # Fallback: convertir manualmente
                    item_dict = {}
                    for column in inspect(item.__class__).columns:
                        value = getattr(item, column.name)
                        if isinstance(value, datetime):
                            value = value.strftime("%Y-%m-%d %H:%M:%S")
                        elif isinstance(value, (list, dict)):
                            value = str(value)
                        item_dict[column.name] = value
                    data.append(item_dict)

        return jsonify(
            {
                "data": data,
                "total": pagination.total,
                "page": page,
                "per_page": per_page,
                "pages": pagination.pages,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/data/<model_name>", methods=["POST"])
@admin_required
def create_model_item(model_name):
    """Crear un nuevo registro"""
    if model_name not in MODELS_CONFIG:
        return jsonify({"error": "Modelo no encontrado"}), 404

    try:
        model = MODELS_CONFIG[model_name]["model"]
        data = request.get_json()

        # Crear instancia
        item = model()

        # Asignar valores
        for key, value in data.items():
            if hasattr(item, key):
                # Manejar campos especiales
                if key == "password" and model_name == "users":
                    item.set_password(value)
                else:
                    setattr(item, key, value)

        db.session.add(item)
        db.session.commit()

        return jsonify({"message": "Registro creado exitosamente", "id": item.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/data/<model_name>/<int:id>", methods=["PUT"])
@admin_required
def update_model_item(model_name, id):
    """Actualizar un registro existente"""
    if model_name not in MODELS_CONFIG:
        return jsonify({"error": "Modelo no encontrado"}), 404

    try:
        model = MODELS_CONFIG[model_name]["model"]
        item = model.query.get(id)

        if not item:
            return jsonify({"error": "Registro no encontrado"}), 404

        data = request.get_json()

        # Actualizar valores
        for key, value in data.items():
            if hasattr(item, key):
                # Manejar campos especiales
                if key == "password" and model_name == "users" and value:
                    item.set_password(value)
                elif key not in ["id", "created_at"]:  # No actualizar campos readonly
                    setattr(item, key, value)

        db.session.commit()

        return jsonify({"message": "Registro actualizado exitosamente", "id": item.id})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/data/<model_name>/<int:id>", methods=["DELETE"])
@admin_required
def delete_model_item(model_name, id):
    """Eliminar un registro"""
    if model_name not in MODELS_CONFIG:
        return jsonify({"error": "Modelo no encontrado"}), 404

    try:
        model = MODELS_CONFIG[model_name]["model"]
        item = model.query.get(id)

        if not item:
            return jsonify({"error": "Registro no encontrado"}), 404

        # ✅ PROTECCIÓN ESPECIAL PARA USUARIOS
        if model_name == "users":
            # No permitir eliminar el usuario actual (admin logueado)
            current_user_id = session.get("user_id")
            if item.id == current_user_id:
                return jsonify({"error": "No puedes eliminarte a ti mismo"}), 400

            # Verificar si el usuario tiene reservas activas
            reservas_activas = Reserva.query.filter_by(
                user_id=item.id, estado="activa"
            ).count()

            if reservas_activas > 0:
                return jsonify({
                    "error": f"No se puede eliminar. El usuario tiene {reservas_activas} reserva(s) activa(s). Cancela o completa las reservas primero."
                }), 400

            # Verificar todas las reservas (activas, completadas, canceladas)
            total_reservas = Reserva.query.filter_by(user_id=item.id).count()

            if total_reservas > 0:
                # Opción 1: Eliminar las reservas en cascada
                # Reserva.query.filter_by(user_id=item.id).delete()
                
                # Opción 2: Mejor - No permitir eliminar usuarios con historial
                return jsonify({
                    "error": f"No se puede eliminar. El usuario tiene {total_reservas} reserva(s) en el historial. Por seguridad, no se permite eliminar usuarios con reservas registradas."
                }), 400

            # Verificar si tiene vehículos registrados
            vehiculos = VehiculoRegistrado.query.filter_by(user_id=item.id).count()
            if vehiculos > 0:
                # Eliminar vehículos registrados primero
                VehiculoRegistrado.query.filter_by(user_id=item.id).delete()

        # ✅ PROTECCIÓN ESPECIAL PARA ESTACIONES
        if model_name == "stations":
            # Verificar si la estación tiene reservas
            reservas = Reserva.query.filter_by(estacion_id=item.id).count()
            if reservas > 0:
                return jsonify({
                    "error": f"No se puede eliminar. La estación tiene {reservas} reserva(s) asociadas."
                }), 400

            # Verificar si tiene conectores
            conectores = Connector.query.filter_by(estacion_id=item.id).count()
            if conectores > 0:
                # Eliminar conectores primero
                Connector.query.filter_by(estacion_id=item.id).delete()

        # ✅ PROTECCIÓN ESPECIAL PARA AUTOS
        if model_name == "autos":
            # Verificar si el auto está registrado por algún usuario
            vehiculos_registrados = VehiculoRegistrado.query.filter_by(autos_id=item.id).count()
            if vehiculos_registrados > 0:
                return jsonify({
                    "error": f"No se puede eliminar. El vehículo está registrado por {vehiculos_registrados} usuario(s)."
                }), 400

        db.session.delete(item)
        db.session.commit()

        return jsonify({"message": "Registro eliminado exitosamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al eliminar: {str(e)}"}), 500


# ============================================
# 📊 ESTADÍSTICAS DEL SISTEMA
# ============================================


@admin_bp.route("/stats", methods=["GET"])
@admin_required
def get_stats():
    """Obtener estadísticas generales del sistema"""
    try:
        stats = {
            "usuarios": {
                "total": User.query.count(),
                "activos": User.query.filter_by(is_active=True).count(),
                "admins": User.query.filter_by(role="admin").count(),
            },
            "reservas": {
                "total": Reserva.query.count(),
                "activas": Reserva.query.filter_by(estado="activa").count(),
                "completadas": Reserva.query.filter_by(estado="completada").count(),
                "canceladas": Reserva.query.filter_by(estado="cancelada").count(),
            },
            "estaciones": {
                "total": Station.query.count(),
                "activas": Station.query.filter_by(activo=True).count(),
            },
            "vehiculos": {
                "total": Auto.query.count(),
                "registrados": VehiculoRegistrado.query.count(),
            },
            "conectores": {
                "total": Connector.query.count(),
                "activos": Connector.query.filter_by(activo=True).count(),
            },
        }

        # Últimas reservas
        latest_reservas = (
            Reserva.query.order_by(Reserva.created_at.desc()).limit(5).all()
        )
        stats["latest_reservas"] = [r.to_dict() for r in latest_reservas]

        # Usuarios más activos (con más reservas)
        active_users = (
            db.session.query(
                User.id,
                User.username,
                db.func.count(Reserva.id).label("reservas_count"),
            )
            .join(Reserva)
            .group_by(User.id)
            .order_by(db.desc("reservas_count"))
            .limit(5)
            .all()
        )

        stats["active_users"] = [
            {"id": u[0], "username": u[1], "reservas": u[2]} for u in active_users
        ]

        return jsonify(stats)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# 🔧 UTILIDADES
# ============================================


@admin_bp.route("/export/<model_name>", methods=["GET"])
@admin_required
def export_data(model_name):
    """Exportar datos a JSON"""
    if model_name not in MODELS_CONFIG:
        return jsonify({"error": "Modelo no encontrado"}), 404

    try:
        model = MODELS_CONFIG[model_name]["model"]
        items = model.query.all()

        data = []
        for item in items:
            if hasattr(item, "to_dict"):
                data.append(item.to_dict())
            else:
                item_dict = {}
                for column in inspect(item.__class__).columns:
                    value = getattr(item, column.name)
                    if isinstance(value, datetime):
                        value = value.strftime("%Y-%m-%d %H:%M:%S")
                    item_dict[column.name] = value
                data.append(item_dict)

        return jsonify(
            {
                "model": model_name,
                "count": len(data),
                "data": data,
                "exported_at": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/bulk-delete/<model_name>", methods=["POST"])
@admin_required
def bulk_delete(model_name):
    """Eliminar múltiples registros"""
    if model_name not in MODELS_CONFIG:
        return jsonify({"error": "Modelo no encontrado"}), 404

    try:
        model = MODELS_CONFIG[model_name]["model"]
        data = request.get_json()
        ids = data.get("ids", [])

        if not ids:
            return jsonify({"error": "No se proporcionaron IDs"}), 400

        deleted_count = model.query.filter(model.id.in_(ids)).delete(
            synchronize_session=False
        )
        db.session.commit()

        return jsonify(
            {"message": f"{deleted_count} registros eliminados", "count": deleted_count}
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500