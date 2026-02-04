from flask import Blueprint, jsonify, request
from models.conectores import Connector

# Blueprint de conectores
conectores_bp = Blueprint("conectores_bp", __name__)


@conectores_bp.route("/api/connectores", methods=["GET"])
def listar_conectores():
    """
    Endpoint de SOLO lectura para conectores.

    Permite:
    - Listar todos los conectores
    - Filtrar por estacion_id (opcional)

    NO:
    - Modifica reservas
    - Afecta frontend actual
    """

    # Leer parámetro opcional
    estacion_id = request.args.get("estacion_id", type=int)

    if estacion_id is not None:
        conectores = Connector.query.filter_by(estacion_id=estacion_id).all()
    else:
        conectores = Connector.query.all()

    # Convertir a JSON
    data = [c.to_dict() for c in conectores]

    return jsonify(data), 200