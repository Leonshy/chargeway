from flask import Blueprint, jsonify, request, session
from models.user import User
from db import db

users_bp = Blueprint("users_bp", __name__)

@users_bp.route("/")
def list_users():
    users = User.query.all()
    return jsonify(
        [{"id": u.id, "username": u.username, "email": u.email} for u in users]
    )

# ============================================
# 🆕 NUEVO: Ruta para actualizar perfil
# ============================================
@users_bp.route("/update", methods=["PUT"])
def update_profile():
    # En lugar de @login_required de Flask-Login, usamos la sesión manual
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Sesión no válida o expirada"}), 401

    data = request.get_json()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # 1. Validar contraseña actual (Seguridad)
    current_password = data.get("current_password")
    if not current_password or not user.check_password(current_password):
        return jsonify({"error": "La contraseña actual es incorrecta"}), 401

    # 2. Actualizar nombre de usuario
    if "username" in data and data["username"]:
        existing = User.query.filter_by(username=data["username"]).first()
        if existing and existing.id != user.id:
            return jsonify({"error": "El nombre de usuario ya está en uso"}), 400
        user.username = data["username"]

    # 3. Actualizar teléfono
    if "phone" in data:
        user.phone = data["phone"]

    # 4. Actualizar contraseña (solo si se envió una nueva)
    if "new_password" in data and data["new_password"]:
        if len(data["new_password"]) < 6:
            return jsonify({"error": "La nueva contraseña es muy corta"}), 400
        user.set_password(data["new_password"])

    try:
        db.session.commit()
        # Retornamos el diccionario del usuario actualizado para el frontend
        return jsonify({
            "message": "Perfil actualizado",
            "user": user.to_dict() # Asegúrate de que tu modelo User tenga to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error update_profile: {e}")
        return jsonify({"error": "Error al guardar en la base de datos"}), 500