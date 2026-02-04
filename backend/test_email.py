"""
Test simple para verificar envío de email (ChargeWay)
Ejecutar: python test_email.py

✅ Lee .env
✅ Muestra configuración (sin exponer contraseña)
✅ Usa email_service_from_env() (misma config que Flask)
✅ Prueba envío con reserva dummy
"""

from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

print("=" * 60)
print("TEST DE CONFIGURACIÓN DE EMAIL")
print("=" * 60)
print()

# Verificar variables de entorno (sin mostrar contraseña)
print("📋 Variables de entorno:")
print(f"  SMTP_SERVER: {os.getenv('SMTP_SERVER')}")
print(f"  SMTP_PORT: {os.getenv('SMTP_PORT')}")
print(f"  EMAIL_USE_SSL: {os.getenv('EMAIL_USE_SSL', 'true')}")
print(f"  EMAIL_USER: {os.getenv('EMAIL_USER')}")
print(
    f"  EMAIL_PASSWORD: {'*' * len(os.getenv('EMAIL_PASSWORD', ''))} ({len(os.getenv('EMAIL_PASSWORD', ''))} caracteres)"
)
print(f"  EMAIL_FROM_NAME: {os.getenv('EMAIL_FROM_NAME', 'Chargeway - no te dejes de mover')}")
print(f"  EMAIL_ENABLED: {os.getenv('EMAIL_ENABLED', 'true')}")
print(f"  EMAIL_TIMEOUT_SECONDS: {os.getenv('EMAIL_TIMEOUT_SECONDS', '12')}")
print(f"  SUPPORT_EMAIL: {os.getenv('SUPPORT_EMAIL', 'soporte@chargeway.com')}")
print()

# Verificar dependencias
try:
    import qrcode  # noqa: F401

    print("✅ qrcode instalado")
except ImportError:
    print("❌ qrcode NO instalado - Ejecuta: pip install qrcode")
    raise SystemExit(1)

try:
    from PIL import Image  # noqa: F401

    print("✅ Pillow instalado")
except ImportError:
    print("❌ Pillow NO instalado - Ejecuta: pip install pillow")
    raise SystemExit(1)

print()
print("=" * 60)
print("INTENTANDO ENVIAR EMAIL DE PRUEBA")
print("=" * 60)
print()

try:
    # Importamos la factory para crear el servicio desde .env
    from services.email_service import email_service_from_env
    from datetime import date, time

    # Creamos el servicio con la misma configuración que usará el backend
    email_service = email_service_from_env()

    # Crear reserva de prueba (objeto simple con los atributos que el servicio necesita)
    class ReservaPrueba:
        id = 1
        codigo = "TEST1234"
        estacion_nombre = "Estación de Prueba YPF"
        estacion_direccion = "Av. Mariscal López 1234, Asunción"
        fecha = date(2026, 2, 10)
        hora_inicio = time(14, 30)
        duracion_horas = 2.0

    reserva = ReservaPrueba()

    destinatario = os.getenv("EMAIL_TEST_TO") or os.getenv("EMAIL_USER")
    if not destinatario:
        print("❌ Falta EMAIL_USER (y no se definió EMAIL_TEST_TO).")
        raise SystemExit(1)

    print(f"📧 Enviando email a: {destinatario}")
    print(f"🧾 From: {os.getenv('EMAIL_FROM_NAME', 'Chargeway - no te dejes de mover')} <{os.getenv('EMAIL_USER')}>")
    print(f"🔐 SSL (465): {os.getenv('EMAIL_USE_SSL', 'true')}")
    print()

    # Intentar enviar
    success, mensaje, codigo = email_service.enviar_confirmacion_reserva(
        destinatario_email=destinatario,
        destinatario_nombre="Usuario de Prueba",
        reserva=reserva,
    )

    print()
    print("=" * 60)
    if success:
        print("✅ ¡EMAIL ENVIADO EXITOSAMENTE!")
        print("=" * 60)
        print()
        print(f"📬 Destinatario: {destinatario}")
        print(f"🔐 Código: {codigo}")
        print()
        print("👉 Revisa tu bandeja de entrada (o SPAM)")
        print(f"   Asunto: ✅ Reserva Confirmada - {codigo}")
    else:
        print("❌ ERROR AL ENVIAR EMAIL")
        print("=" * 60)
        print()
        print(f"Mensaje de error: {mensaje}")
        print()
        print("💡 Posibles causas:")
        print("1. Host SMTP incorrecto (probá smtp.naranja.com.py o mail.naranja.com.py)")
        print("2. Puerto bloqueado (465) o red restringida")
        print("3. Credenciales incorrectas o bloqueo por IP")
        print("4. Certificado SSL no coincide con el host usado")
    print("=" * 60)

except Exception as e:
    print(f"❌ ERROR INESPERADO: {e}")
    print()
    import traceback

    traceback.print_exc()