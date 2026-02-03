from flask import Blueprint, jsonify
from services.openchargemap import obtener_estaciones

estaciones_bp = Blueprint("estaciones_bp", __name__)


@estaciones_bp.route("/")
def estaciones():
    return jsonify(obtener_estaciones())
