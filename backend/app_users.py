# app_users.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash  # Para hashear contraseñas
import os


app = Flask(__name__)
# Obtiene la ruta del directorio donde está este script
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Ruta absoluta de la DB dentro de backend/instance
DB_PATH = os.path.join(BASE_DIR, "instance", "users.db")

# Configuración de SQLAlchemy con ruta absoluta
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Creamos el objeto SQLAlchemy
db = SQLAlchemy(app)

# Definimos el modelo de usuario
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID del usuario
    username = db.Column(db.String(50), unique=True, nullable=False)  # Nombre de usuario
    phone = db.Column(db.String(20), unique=True, nullable=True)  # Teléfono
    email = db.Column(db.String(100), unique=True, nullable=False)  # Correo
    password_hash = db.Column(db.String(128), nullable=False)  # Contraseña hasheada
    is_active = db.Column(db.Boolean, default=True)  # Estado del usuario
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Fecha de creación

    # Método para guardar la contraseña de manera segura
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Método para verificar la contraseña
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
# -----------------------------
# Inicializar base de datos
@app.before_first_request
def init_db():
    db.create_all()
    print("Base de datos y tabla 'User' creadas correctamente.")

# -----------------------------
# Ruta para agregar usuario (POST)
@app.route("/add_user", methods=["POST"])
def route_add_user():
    data = request.form or request.json  # acepta form-data o JSON
    username = data.get("username")
    phone = data.get("phone")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    # Verificar si existe
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "Usuario o correo ya existe"}), 400

    new_user = User(username=username, phone=phone, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"Usuario {username} agregado correctamente"}), 201

# -----------------------------
# Ruta para listar todos los usuarios (GET)
@app.route("/list_users", methods=["GET"])
def route_list_users():
    users = User.query.all()
    users_list = [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "phone": u.phone,
            "active": u.is_active,
            "created": u.created_at
        }
        for u in users
    ]
    return jsonify(users_list), 200

# -----------------------------
# Ruta de prueba
@app.route("/")
def home():
    return "<h2>Backend de usuarios activo</h2>"

# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)

# Función para inicializar la base de datos
def init_db():
    with app.app_context():
        db.create_all()  # Crea las tablas si no existen
        print("Base de datos y tabla 'User' creadas correctamente.")

# Función para agregar un nuevo usuario
def add_user(username, phone, email, password):
    with app.app_context():
        # Verificamos si ya existe el usuario o correo
        if User.query.filter((User.username == username) | (User.email == email)).first():
            print("Error: El usuario o correo ya existe.")
            return False

        # Creamos el objeto usuario
        new_user = User(username=username, phone=phone, email=email)
        new_user.set_password(password)  # Hasheamos la contraseña

        db.session.add(new_user)  # Agregamos a la sesión
        db.session.commit()       # Guardamos los cambios en la DB
        print(f"Usuario {username} agregado correctamente.")
        return True

# Función para listar todos los usuarios
def list_users():
    with app.app_context():
        users = User.query.all()
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Phone: {user.phone}, Active: {user.is_active}, Created: {user.created_at}")

# Código de prueba
if __name__ == "__main__":
    init_db()  # Crea la base de datos y la tabla
    # Ejemplo de agregar un usuario
    add_user("mariel123", "0981234567", "mariel@example.com", "miContraseñaSegura")
    list_users()  # Muestra los usuarios en la consola