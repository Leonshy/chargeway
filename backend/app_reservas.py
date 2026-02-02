# Importamos Flask para crear la app y request/jsonify/CORS para leer datos y responder JSON
from flask import Flask, request, jsonify

# Importamos SQLAlchemy para manejar la base de datos de forma sencilla (ORM)
from flask_sqlalchemy import SQLAlchemy

#importamos flask_cors permite autorizar solicitudes desde otros orígenes (puertos)
from flask_cors import CORS

# Importamos datetime para guardar fechas/horas en la BD
from datetime import datetime

from pathlib import Path

# Creamos la aplicación Flask
app = Flask(__name__)
CORS(app)

# 1) BASE_DIR = carpeta donde vive este archivo (backend/)
BASE_DIR = Path(__file__).resolve().parent

# 2) instance_dir = backend/instance
INSTANCE_DIR = BASE_DIR / "instance"

# 3) Aseguramos que exista (si no existe, la crea)
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

# 4) Path del archivo sqlite: backend/instance/reservas.db
DB_PATH = INSTANCE_DIR / "reservas.db"

# 5) URI con path ABSOLUTO (esto evita problemas de rutas relativas)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Inicializamos SQLAlchemy con la app (esto conecta Flask con la BD)
db = SQLAlchemy(app)

# ---------------------------------------------------------
# MODELO
# ---------------------------------------------------------


# Creamos un modelo (tabla) para guardar intervalos bloqueados:
# - Reservas hechas
# - Horarios deshabilitados
class BlockedSlot(db.Model):
    __tablename__ = "blocked_slots"

    id = db.Column(db.Integer, primary_key=True)

    # 🔌 Conector que se reserva (CLAVE DEL SISTEMA)
    connector_id = db.Column(db.Integer, nullable=False)

    # 👤 Usuario que hizo la reserva
    # Puede ser NULL cuando el bloqueo es por mantenimiento
    user_id = db.Column(db.Integer, nullable=True)

    # ⏰ Intervalo bloqueado
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    # reserved = reserva de usuario
    # disabled = mantenimiento / fuera de servicio
    kind = db.Column(db.String(20), nullable=False, default="reserved")

    # nota opcional
    note = db.Column(db.String(200), nullable=True)
# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def parse_datetime(value: str) -> datetime:
    """
    Convierte strings de fecha/hora del frontend a datetime.
    Soporta:
    - 'YYYY-MM-DDTHH:MM'  (input datetime-local)
    - 'YYYY-MM-DD HH:MM'
    """
    if not value:
        raise ValueError("datetime vacío")

    # Normalizamos el formato reemplazando la T por espacio
    normalized = value.replace("T", " ")

    # Convertimos a datetime real
    return datetime.strptime(normalized, "%Y-%m-%d %H:%M")

# ---------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------

#@app.route("/init-db")
#def init_db():
#    # db.create_all() crea todas las tablas definidas con db.Model
#    # Solo las crea si no existen (no debería borrar nada existente)
#    db.create_all()
#
#    #Respondemos JSON para confirmar que se ejecutó bien
#    return jsonify({
#        "message": "OK - SQLite creado y tablas listas",
#        "db_file": "reservas.db",
#        "tables": ["blocked_slots"]
#    })

@app.route("/api/reserve", methods=["POST"])
def create_reservation():
    """
    Recibe una reserva desde el frontend y la guarda en la BD.
    La reserva se hace SIEMPRE por connector_id.
    """
    print(">>> /api/reserve fue llamado") #solo para pruebas
    data = request.get_json(silent=True) or {}
    # 1) Leer JSON del request
    data = request.get_json(silent=True) or {}
    print(">>> DATA RECIBIDA:", data) ## solo para pruebas
    connector_id = data.get("connector_id")
    user_id = data.get("user_id")
    start_raw = data.get("start_time")
    end_raw = data.get("end_time")

    # 2) Validaciones básicas (datos obligatorios)
    if not connector_id:
        return jsonify({"error": "connector_id es requerido"}), 400

    if not user_id:
        return jsonify({"error": "user_id es requerido"}), 400

    if not start_raw or not end_raw:
        return jsonify({"error": "start_time y end_time son requeridos"}), 400

    # 3) Parsear fechas
    try:
        start_time = parse_datetime(start_raw)
        end_time = parse_datetime(end_raw)
    except Exception:
        return jsonify({"error": "Formato de fecha inválido"}), 400

    if end_time <= start_time:
        return jsonify({"error": "end_time debe ser mayor que start_time"}), 400

    # 4) Verificar solapamiento (LA REGLA MÁS IMPORTANTE)
    conflict = BlockedSlot.query.filter(
        BlockedSlot.connector_id == connector_id,
        BlockedSlot.start_time < end_time,
        BlockedSlot.end_time > start_time
    ).first()

    if conflict:
        return jsonify({
            "error": "Este conector ya está reservado en ese horario",
            "conflict": {
                "start_time": conflict.start_time.isoformat(timespec="minutes"),
                "end_time": conflict.end_time.isoformat(timespec="minutes")
            }
        }), 409

    # 5) Crear la reserva
    reservation = BlockedSlot(
        connector_id=connector_id,
        user_id=user_id,
        start_time=start_time,
        end_time=end_time,
        kind="reserved"
    )

    # 6) Guardar en la BD
    db.session.add(reservation)
    db.session.commit()

    # 7) Responder al frontend
    return jsonify({
        "message": "Reserva creada correctamente",
        "reservation": {
            "id": reservation.id,
            "connector_id": reservation.connector_id,
            "user_id": reservation.user_id,
            "start_time": reservation.start_time.isoformat(timespec="minutes"),
            "end_time": reservation.end_time.isoformat(timespec="minutes")
        }
    }), 201

# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    # app.run(debug=True) levanta el servidor local en modo debug
    # debug=True reinicia automáticamente si haces cambios
    app.run(debug=True)