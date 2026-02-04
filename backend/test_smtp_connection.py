import socket
import smtplib
import ssl
from dotenv import load_dotenv
import os

# Cargar variables
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

print("=" * 70)
print("PRUEBA DE CONEXIÓN AL SERVIDOR SMTP")
print("=" * 70)

# Prueba 1: Conexión de socket básica
print(f"\n1️⃣ Probando conexión de socket a {SMTP_SERVER}:{SMTP_PORT}...")
try:
    sock = socket.create_connection((SMTP_SERVER, SMTP_PORT), timeout=10)
    print(f"   ✅ Socket conectado exitosamente")
    sock.close()
except Exception as e:
    print(f"   ❌ Error de conexión: {e}")
    print("   💡 Verifica tu conexión a internet o firewall")
    exit(1)

# Prueba 2: Conexión SMTP con SSL
print(f"\n2️⃣ Probando conexión SMTP SSL...")
try:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    with smtplib.SMTP_SSL(
        SMTP_SERVER, SMTP_PORT, context=context, timeout=10
    ) as server:
        print(f"   ✅ Conexión SMTP SSL establecida")

        # Prueba 3: Autenticación
        print(f"\n3️⃣ Probando autenticación con usuario: {EMAIL_USER}...")
        try:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            print(f"   ✅ Autenticación exitosa")
            print(f"\n{'='*70}")
            print(
                "🎉 TODAS LAS PRUEBAS PASARON - El servidor está funcionando correctamente"
            )
            print(f"{'='*70}")
        except smtplib.SMTPAuthenticationError as e:
            print(f"   ❌ Error de autenticación: {e}")
            print(f"   💡 Verifica el usuario y contraseña en tu archivo .env")
            print(f"   💡 Usuario: {EMAIL_USER}")
            print(
                f"   💡 Password: {'*' * len(EMAIL_PASSWORD)} (longitud: {len(EMAIL_PASSWORD)})"
            )
        except Exception as e:
            print(f"   ❌ Error inesperado en autenticación: {e}")

except Exception as e:
    print(f"   ❌ Error de conexión SMTP: {e}")
    print(f"   💡 Posibles causas:")
    print(f"      - Certificado SSL inválido")
    print(f"      - Puerto incorrecto (prueba 587 con STARTTLS)")
    print(f"      - Firewall bloqueando la conexión")

print("\n" + "=" * 70)
