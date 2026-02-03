from flask import Blueprint, jsonify

reservas_bp = Blueprint("reservas", __name__)


@reservas_bp.route("/api/reservas")
def reservas():
    return jsonify({"message": "Reservas OK"})
