"""
Test simple para verificar envío de email
Ejecutar: python test_email_simple.py
"""

from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

print("=" * 60)
print("TEST DE CONFIGURACIÓN DE EMAIL")
print("=" * 60)
print()

# Verificar variables
print("📋 Variables de entorno:")
print(f"  SMTP_SERVER: {os.getenv('SMTP_SERVER')}")
print(f"  SMTP_PORT: {os.getenv('SMTP_PORT')}")
print(f"  EMAIL_USER: {os.getenv('EMAIL_USER')}")
print(
    f"  EMAIL_PASSWORD: {'*' * len(os.getenv('EMAIL_PASSWORD', ''))} ({len(os.getenv('EMAIL_PASSWORD', ''))} caracteres)"
)
print(f"  EMAIL_ENABLED: {os.getenv('EMAIL_ENABLED')}")
print()

# Verificar que las dependencias estén instaladas
try:
    import qrcode

    print("✅ qrcode instalado")
except ImportError:
    print("❌ qrcode NO instalado - Ejecuta: pip install qrcode")
    exit(1)

try:
    from PIL import Image

    print("✅ Pillow instalado")
except ImportError:
    print("❌ Pillow NO instalado - Ejecuta: pip install pillow")
    exit(1)

print()
print("=" * 60)
print("INTENTANDO ENVIAR EMAIL DE PRUEBA")
print("=" * 60)
print()

try:
    from services.email_service import EmailService
    from datetime import date, time

    # Configurar servicio
    email_service = EmailService(
        smtp_server=os.getenv("SMTP_SERVER"),
        smtp_port=int(os.getenv("SMTP_PORT")),
        email_user=os.getenv("EMAIL_USER"),
        email_password=os.getenv("EMAIL_PASSWORD"),
    )

    # Crear reserva de prueba
    class ReservaPrueba:
        id = 1
        codigo = "TEST1234"
        estacion_nombre = "Estación de Prueba YPF"
        estacion_direccion = "Av. Mariscal López 1234, Asunción"
        fecha = date(2026, 2, 10)
        hora_inicio = time(14, 30)
        duracion_horas = 2.0

    reserva = ReservaPrueba()

    print(f"📧 Enviando email a: {os.getenv('EMAIL_USER')}")
    print()

    # Intentar enviar
    success, mensaje, codigo = email_service.enviar_confirmacion_reserva(
        destinatario_email=os.getenv("EMAIL_USER"),
        destinatario_nombre="Usuario de Prueba",
        reserva=reserva,
    )

    print()
    print("=" * 60)
    if success:
        print("✅ ¡EMAIL ENVIADO EXITOSAMENTE!")
        print("=" * 60)
        print()
        print(f"📬 Destinatario: {os.getenv('EMAIL_USER')}")
        print(f"🔐 Código: {codigo}")
        print()
        print("👉 Revisa tu bandeja de entrada (o SPAM)")
        print("   Asunto: ✅ Reserva Confirmada - TEST1234")
    else:
        print("❌ ERROR AL ENVIAR EMAIL")
        print("=" * 60)
        print()
        print(f"Mensaje de error: {mensaje}")
        print()
        print("💡 Posibles causas:")
        print("1. Contraseña incorrecta (debe ser App Password de 16 caracteres)")
        print("2. Email incorrecto")
        print("3. Verificación en 2 pasos no activada en Gmail")
        print("4. Problemas de conexión a internet")
    print("=" * 60)

except Exception as e:
    print(f"❌ ERROR INESPERADO: {e}")
    print()
    import traceback

    traceback.print_exc()
