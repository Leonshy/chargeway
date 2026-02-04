from flask import Blueprint, request, jsonify, session
from db import db
from models.user import User

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Credenciales inválidas"}), 401

    session["user_id"] = user.id
    return jsonify(
        {
            "message": "Login exitoso",
            "user": {"id": user.id, "username": user.username, "email": user.email},
        }
    )


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not all(k in data for k in ["username", "email", "password"]):
        return jsonify({"error": "Faltan datos"}), 400

    if User.query.filter(
        (User.username == data["username"]) | (User.email == data["email"])
    ).first():
        return jsonify({"error": "Usuario o email ya existe"}), 400

    user = User(username=data["username"], email=data["email"], phone=data.get("phone"))
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id

    return jsonify(
        {
            "message": "Registro exitoso",
            "user": {"id": user.id, "username": user.username, "email": user.email},
        }
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logout exitoso"})
