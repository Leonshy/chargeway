from flask import Flask
from flask_cors import CORS
from config import Config
from db import db
from flask import render_template

from routes.auth_bp import auth_bp
from routes.estaciones_bp import estaciones_bp
from routes.ev_bp import ev_bp
from routes.reservas_bp import reservas_bp
from routes.users_bp import users_bp
from services.openchargemap import generar_mapa

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar extensiones
CORS(app, supports_credentials=True)
db.init_app(app)

# Crear tablas si no existen
with app.app_context():
    db.create_all()

# Registrar Blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(estaciones_bp, url_prefix="/api/estaciones")
app.register_blueprint(ev_bp)
app.register_blueprint(reservas_bp)
app.register_blueprint(users_bp, url_prefix="/api/users")


# Endpoint para el mapa
@app.route("/api/mapa")
def mapa():
    return generar_mapa()


# Endpoint para verificar autenticación
@app.route("/api/auth/check")
def check_auth():
    from flask import session, jsonify

    if "user_id" in session:
        from models.user import User

        user = User.query.get(session["user_id"])
        if user:
            return jsonify(
                {
                    "authenticated": True,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                }
            )
    return jsonify({"authenticated": False})

@app.route("/")
def index():
    mapa_html = generar_mapa()
    return render_template("index.html", mapa_html=mapa_html)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
