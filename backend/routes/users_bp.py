from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user # Asumiendo flask_login
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
@login_required
def update_profile():
    data = request.get_json()
    user = User.query.get(current_user.id)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Validar contraseña actual para seguridad
    current_password = data.get("current_password")
    if not current_password or not user.check_password(current_password):
        return jsonify({"error": "La contraseña actual es incorrecta"}), 401

    # Actualizar datos
    if "username" in data and data["username"]:
        existing = User.query.filter_by(username=data["username"]).first()
        if existing and existing.id != user.id:
            return jsonify({"error": "El usuario ya existe"}), 400
        user.username = data["username"]

    if "phone" in data:
        user.phone = data["phone"]

    if "new_password" in data and data["new_password"]:
        if len(data["new_password"]) < 6:
            return jsonify({"error": "Mínimo 6 caracteres para la contraseña"}), 400
        user.set_password(data["new_password"])

    try:
        db.session.commit()
        return jsonify({"message": "Actualizado", "user": user.to_dict(include_role=True)})
    except:
        db.session.rollback()
        return jsonify({"error": "Error en BD"}), 500