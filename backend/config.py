from pathlib import Path
import os

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
    
    # ============================================
    # CONFIGURACIÓN DE EMAIL
    # ============================================
    
    # Servidor SMTP (Gmail por defecto)
    # Para Gmail: smtp.gmail.com
    # Para Outlook: smtp-mail.outlook.com
    # Para Yahoo: smtp.mail.yahoo.com
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    
    # Puerto SMTP (587 para TLS, 465 para SSL)
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    
    # Email desde el cual se enviarán las confirmaciones
    EMAIL_USER = os.getenv('EMAIL_USER', 'tu-email@gmail.com')
    
    # Contraseña del email o App Password (recomendado para Gmail)
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'tu-contraseña-aqui')
    
    # Habilitar/deshabilitar envío de emails (útil para desarrollo)
    EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'true').lower() == 'true'
    
    # Email de soporte que aparecerá en los correos
    SUPPORT_EMAIL = 'soporte@chargeway.com'