# Importamos Flask para crear la app y request/jsonify para leer datos y responder JSON
from flask import Flask, request, jsonify

# Importamos SQLAlchemy para manejar la base de datos de forma sencilla (ORM)
from flask_sqlalchemy import SQLAlchemy

# Importamos datetime para guardar fechas/horas en la BD
from datetime import datetime

from pathlib import Path

# Creamos la aplicación Flask
app = Flask(__name__)

# Configuramos la BD SQLite:
# - "sqlite:///reservas.db" significa: crear/usar un archivo "reservas.db" en la carpeta del proyecto
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///reservas.db"

# Desactivamos el track modifications para evitar warnings y ahorrar recursos
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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


# Creamos un modelo (tabla) para guardar intervalos bloqueados:
# - Reservas hechas
# - Horarios deshabilitados
class BlockedSlot(db.Model):
    # Nombre real de la tabla en la BD
    __tablename__ = "blocked_slots"
    id = db.Column(db.Integer, primary_key=True)# ID autoincremental (clave primaria)
    station_id = db.Column(db.String(64), nullable=False)# station_id: por ahora lo guardamos como texto porque todavía no tenés

    # start_time y end_time marcan el intervalo bloqueado
    # Ej: 2026-02-02 10:00 hasta 2026-02-02 11:00
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    # kind indica el tipo de bloqueo:
    # - "reserved" (reservado por alguien)
    # - "disabled" (bloqueado por mantenimiento)
    kind = db.Column(db.String(20), nullable=False, default="reserved")

    # nota opcional: ejemplo "mantenimiento", "evento", etc.
    note = db.Column(db.String(200), nullable=True)

@app.route("/init-db")
def init_db():
    # db.create_all() crea todas las tablas definidas con db.Model
    # Solo las crea si no existen (no debería borrar nada existente)
    db.create_all()

    # Respondemos JSON para confirmar que se ejecutó bien
    return jsonify({
        "message": "OK - SQLite creado y tablas listas",
        "db_file": "reservas.db",
        "tables": ["blocked_slots"]
    })
if __name__ == "__main__":
    # app.run(debug=True) levanta el servidor local en modo debug
    # debug=True reinicia automáticamente si haces cambios
    app.run(debug=True)