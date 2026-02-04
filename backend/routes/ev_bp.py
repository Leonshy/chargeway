from flask import Blueprint, jsonify
from services.vehiculos_db import get_conn

ev_bp = Blueprint("ev", __name__)


@ev_bp.route("/api/vehiculos/marcas")
def marcas():
    try:
        conn = get_conn()
        rows = conn.execute("SELECT DISTINCT marca FROM autos").fetchall()
        conn.close()
        return jsonify([r["marca"] for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
