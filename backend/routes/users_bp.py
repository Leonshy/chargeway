from flask import Blueprint, jsonify
from models.user import User

users_bp = Blueprint("users_bp", __name__)


@users_bp.route("/")
def list_users():
    users = User.query.all()
    return jsonify(
        [{"id": u.id, "username": u.username, "email": u.email} for u in users]
    )
