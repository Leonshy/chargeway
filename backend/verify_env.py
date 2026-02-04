import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("=" * 70)
print("VERIFICACIÓN DE VARIABLES DE ENTORNO")
print("=" * 70)

variables = [
    "SMTP_SERVER",
    "SMTP_PORT",
    "EMAIL_USER",
    "EMAIL_PASSWORD",
    "EMAIL_USE_SSL",
    "EMAIL_ENABLED",
    "EMAIL_SSL_VERIFY",
    "EMAIL_FROM_NAME",
    "SUPPORT_EMAIL",
    "EMAIL_TIMEOUT_SECONDS",
]

all_ok = True
for var in variables:
    value = os.getenv(var)
    if value:
        # Ocultar password por seguridad
        if "PASSWORD" in var:
            display_value = f"{'*' * len(value)} (longitud: {len(value)})"
        else:
            display_value = value
        print(f"✅ {var}: {display_value}")
    else:
        print(f"❌ {var}: NO CONFIGURADO")
        all_ok = False

print("=" * 70)
if all_ok:
    print("✅ TODAS LAS VARIABLES ESTÁN CONFIGURADAS")
    print("\nProcede a ejecutar: python test_email.py")
else:
    print("❌ FALTAN VARIABLES - Revisa tu archivo .env")

print("=" * 70)
