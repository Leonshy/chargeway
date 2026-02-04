"""
Script de prueba específico para mail.naranja.com.py
Ejecutar: python test_naranja_email.py
"""

import os
import sys

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("PRUEBA DE EMAIL CON mail.naranja.com.py")
print("=" * 70)

# ============================================
# 1. CARGAR VARIABLES DE ENTORNO
# ============================================
print("\n1️⃣ CARGANDO VARIABLES DE ENTORNO")
print("-" * 70)

from dotenv import load_dotenv

load_dotenv()

# Verificar que están configuradas
config = {
    "SMTP_SERVER": os.getenv("SMTP_SERVER"),
    "SMTP_PORT": os.getenv("SMTP_PORT"),
    "EMAIL_USER": os.getenv("EMAIL_USER"),
    "EMAIL_PASSWORD": os.getenv("EMAIL_PASSWORD"),
    "EMAIL_USE_SSL": os.getenv("EMAIL_USE_SSL"),
    "EMAIL_ENABLED": os.getenv("EMAIL_ENABLED"),
    "EMAIL_SSL_VERIFY": os.getenv("EMAIL_SSL_VERIFY"),
}

print("\nConfiguración detectada:")
for key, value in config.items():
    if "PASSWORD" in key:
        display_value = "***" if value else "❌ NO CONFIGURADO"
    else:
        display_value = value if value else "❌ NO CONFIGURADO"

    status = "✅" if value else "❌"
    print(f"{status} {key}: {display_value}")

# Validar configuración mínima
if not all(
    [
        config["SMTP_SERVER"],
        config["SMTP_PORT"],
        config["EMAIL_USER"],
        config["EMAIL_PASSWORD"],
    ]
):
    print("\n❌ ERROR: Faltan variables de entorno requeridas")
    print("Crea un archivo .env con:")
    print(
        """
SMTP_SERVER=mail.naranja.com.py
SMTP_PORT=465
EMAIL_USE_SSL=true
EMAIL_USER=chargeway@naranja.com.py
EMAIL_PASSWORD=tu-password-aqui
EMAIL_FROM_NAME=Chargeway - no te dejes de mover
EMAIL_ENABLED=true
EMAIL_TIMEOUT_SECONDS=12
EMAIL_SSL_VERIFY=false
SUPPORT_EMAIL=leodav.amarilla@gmail.com
    """
    )
    sys.exit(1)

# ============================================
# 2. PRUEBA DE CONEXIÓN SMTP DIRECTA
# ============================================
print("\n2️⃣ PROBANDO CONEXIÓN SMTP DIRECTA")
print("-" * 70)

import smtplib
import ssl

try:
    smtp_server = config["SMTP_SERVER"]
    smtp_port = int(config["SMTP_PORT"])
    email_user = config["EMAIL_USER"]
    email_password = config["EMAIL_PASSWORD"]

    print(f"🔄 Conectando a {smtp_server}:{smtp_port}...")

    # Para puerto 465 usamos SMTP_SSL
    if smtp_port == 465:
        print("   Usando SMTP_SSL (puerto 465)")

        # Verificar si debemos validar SSL
        verify_ssl = config.get("EMAIL_SSL_VERIFY", "false").lower() == "true"
        print(f"   Verificación SSL: {verify_ssl}")

        if verify_ssl:
            context = ssl.create_default_context()
        else:
            context = ssl._create_unverified_context()

        server = smtplib.SMTP_SSL(
            host=smtp_server, port=smtp_port, timeout=12, context=context
        )
        print("✅ Conexión SSL establecida")
    else:
        print("   Usando SMTP con STARTTLS (puerto 587)")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=12)
        server.starttls()
        print("✅ Conexión TLS establecida")

    # Intentar login
    print(f"🔑 Autenticando como {email_user}...")
    server.login(email_user, email_password)
    print("✅ Autenticación exitosa!")

    server.quit()
    print("✅ Prueba de conexión SMTP: OK\n")

except smtplib.SMTPAuthenticationError as e:
    print(f"❌ Error de autenticación: {e}")
    print("\n💡 Verifica:")
    print("   - EMAIL_USER es correcto: chargeway@naranja.com.py")
    print("   - EMAIL_PASSWORD es correcto")
    sys.exit(1)

except ssl.SSLError as e:
    print(f"❌ Error SSL: {e}")
    print("\n💡 Intenta configurar:")
    print("   EMAIL_SSL_VERIFY=false")
    sys.exit(1)

except Exception as e:
    print(f"❌ Error de conexión: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# ============================================
# 3. PROBAR EmailService
# ============================================
print("\n3️⃣ PROBANDO EmailService")
print("-" * 70)

try:
    from services.email_service import email_service_from_env

    print("🔄 Creando EmailService...")
    email_service = email_service_from_env()

    print("\nConfiguración del servicio:")
    print(f"   SMTP Server: {email_service.smtp_server}")
    print(f"   SMTP Port: {email_service.smtp_port}")
    print(f"   Email User: {email_service.email_user}")
    print(f"   Use SSL: {email_service.use_ssl}")
    print(f"   Enabled: {email_service.enabled}")
    print(f"   Timeout: {email_service.timeout_seconds}s")

    if not email_service.enabled:
        print("\n⚠️ EMAIL_ENABLED=false - Los emails no se enviarán")
        print("   Cambia EMAIL_ENABLED=true en tu .env")
        sys.exit(1)

    print("✅ EmailService creado correctamente")

except Exception as e:
    print(f"❌ Error al crear EmailService: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# ============================================
# 4. PROBAR ENVÍO CON UNA RESERVA REAL
# ============================================
print("\n4️⃣ PROBANDO ENVÍO CON RESERVA DE LA BD")
print("-" * 70)

try:
    from app import create_app
    from models.reserva import Reserva
    from models.user import User

    app = create_app()

    with app.app_context():
        # Buscar última reserva
        reserva = Reserva.query.order_by(Reserva.id.desc()).first()

        if not reserva:
            print("⚠️ No hay reservas en la base de datos")
            print("   Crea una reserva primero desde la aplicación")
            sys.exit(1)

        print(f"✅ Encontrada reserva ID: {reserva.id}")
        print(f"   Código: {reserva.codigo}")
        print(f"   Estado: {reserva.estado}")

        # Buscar usuario
        user = User.query.get(reserva.user_id)
        if not user:
            print(f"❌ Usuario {reserva.user_id} no encontrado")
            sys.exit(1)

        print(f"✅ Usuario: {user.username}")
        print(f"   Email: {user.email}")

        if not user.email:
            print("❌ El usuario no tiene email configurado")
            sys.exit(1)

        # Preguntar si desea enviar el email
        print(f"\n📧 ¿Deseas enviar un email de prueba a {user.email}?")
        respuesta = input("   Escribe 'si' para continuar: ").strip().lower()

        if respuesta != "si":
            print("❌ Prueba cancelada")
            sys.exit(0)

        print(f"\n🔄 Enviando email...")
        print("-" * 70)

        success, mensaje, codigo = email_service.enviar_confirmacion_reserva(
            destinatario_email=user.email,
            destinatario_nombre=user.username,
            reserva=reserva,
        )

        print("-" * 70)

        if success:
            print("\n🎉 ✅ EMAIL ENVIADO EXITOSAMENTE!")
            print(f"   Destinatario: {user.email}")
            print(f"   Código: {codigo}")
            print(f"   Mensaje: {mensaje}")

            # Actualizar codigo_enviado
            print(f"\n💾 Actualizando campo codigo_enviado...")
            reserva.codigo_enviado = True
            from db import db

            db.session.commit()
            print("✅ Base de datos actualizada")

            print("\n📬 Revisa la bandeja de entrada de:", user.email)
            print("   (También revisa la carpeta de spam)")

        else:
            print(f"\n❌ ERROR AL ENVIAR EMAIL")
            print(f"   Mensaje: {mensaje}")

except Exception as e:
    print(f"\n❌ Error en la prueba: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# ============================================
# RESUMEN FINAL
# ============================================
print("\n" + "=" * 70)
print("RESUMEN")
print("=" * 70)

if success:
    print(
        """
✅ TODO ESTÁ FUNCIONANDO CORRECTAMENTE

Siguiente paso:
1. Crea una nueva reserva desde tu frontend
2. Verifica que el email llegue automáticamente
3. Revisa en la BD que codigo_enviado = 1

Si el email no llega automáticamente al crear reservas:
- Verifica que estés usando el archivo reservas_bp.py corregido
- Reinicia el servidor Flask
- Revisa los logs de la consola del servidor
"""
    )
else:
    print(
        """
❌ HAY UN PROBLEMA

Revisa:
1. Las credenciales en .env (EMAIL_USER y EMAIL_PASSWORD)
2. La configuración del servidor mail.naranja.com.py
3. Los logs arriba para ver el error específico

Contacta a tu proveedor de email si persiste el problema.
"""
    )

print("=" * 70)
