from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"

# Crear el directorio instance si no existe
INSTANCE_DIR.mkdir(exist_ok=True)

# Ruta ABSOLUTA a la única base de datos
DB_PATH = INSTANCE_DIR / "chargeway.db"

class Config:
    SECRET_KEY = "super-secret-key"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
