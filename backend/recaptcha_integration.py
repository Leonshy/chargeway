# ============================================
# 📝 CÓDIGO PARA AGREGAR AL BACKEND (Flask)
# ============================================

# 1. Instalar la librería para validar reCAPTCHA:
#    pip install requests --break-system-packages

# 2. Agregar a tu config.py o donde tengas las configuraciones:
"""
RECAPTCHA_SECRET_KEY = "6Lc-OGAsAAAAAPPwn7UOnRsCUXxLUJ7E9EduNYjz"  # 👈 Secret key de Google reCAPTCHA
"""

# 3. Agregar esta función helper (puedes crear un archivo utils/recaptcha.py):

import requests
from flask import current_app

def verificar_recaptcha(token):
    """
    Verifica el token de reCAPTCHA con Google
    
    Args:
        token (str): Token recibido del frontend
        
    Returns:
        tuple: (success: bool, error_message: str)
    """
    if not token:
        return False, "Token de captcha no proporcionado"
    
    secret_key = current_app.config.get('RECAPTCHA_SECRET_KEY')
    
    if not secret_key:
        return False, "Configuración de captcha no disponible"
    
    # Verificar con Google
    verification_url = "https://www.google.com/recaptcha/api/siteverify"
    
    try:
        response = requests.post(verification_url, data={
            'secret': secret_key,
            'response': token
        })
        
        result = response.json()
        
        if result.get('success'):
            return True, None
        else:
            error_codes = result.get('error-codes', [])
            return False, f"Captcha inválido: {', '.join(error_codes)}"
            
    except Exception as e:
        return False, f"Error al verificar captcha: {str(e)}"


# 4. Modificar tu endpoint de registro en auth_bp.py:

# ANTES (ejemplo de cómo podría estar tu código actual):
"""
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")
    
    # ... validaciones ...
    
    # Crear usuario
    user = User(username=username, email=email, phone=phone)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "Usuario creado", "user": user.to_dict()})
"""

# DESPUÉS (con validación de captcha):
"""
from utils.recaptcha import verificar_recaptcha  # Importar la función

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    # ============================================
    # ✅ VALIDAR CAPTCHA PRIMERO
    # ============================================
    recaptcha_token = data.get("recaptcha_token")
    
    captcha_valido, error_captcha = verificar_recaptcha(recaptcha_token)
    
    if not captcha_valido:
        return jsonify({"error": error_captcha or "Captcha inválido"}), 400
    
    # Si el captcha es válido, continuar con el registro normal
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")
    
    # ... resto de validaciones y creación de usuario ...
    
    # Crear usuario
    user = User(username=username, email=email, phone=phone)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "Usuario creado", "user": user.to_dict()})
"""