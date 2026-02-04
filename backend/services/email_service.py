import os
import ssl
import smtplib
from io import BytesIO
from email.utils import formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import qrcode


class EmailService:
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        email_user: str,
        email_password: str,
        *,
        from_name: str = "Chargeway - no te dejes de mover",
        use_ssl: bool = True,
        enabled: bool = True,
        timeout_seconds: int = 12,
        support_email: str = "soporte@chargeway.com",
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_user = email_user
        self.email_password = email_password
        self.from_name = from_name
        self.use_ssl = use_ssl
        self.enabled = enabled
        self.timeout_seconds = timeout_seconds
        self.support_email = support_email

    def _open_smtp_connection(self):
        # ✅ MEJORA: Forzar SSL si el puerto es 465
        if self.smtp_port == 465:
            self.use_ssl = True

        if self.use_ssl:
            verify_ssl = os.getenv("EMAIL_SSL_VERIFY", "true").lower() == "true"
            context = (
                ssl.create_default_context()
                if verify_ssl
                else ssl._create_unverified_context()
            )

            # ✅ MEJORA: Logging para debugging
            print(f"🔐 Conectando SMTP_SSL a {self.smtp_server}:{self.smtp_port}")
            print(f"   SSL Verify: {verify_ssl}")

            return smtplib.SMTP_SSL(
                host=self.smtp_server,
                port=self.smtp_port,
                timeout=self.timeout_seconds,
                context=context,
            )

        # Modo TLS (puerto 587)
        print(f"🔐 Conectando SMTP+TLS a {self.smtp_server}:{self.smtp_port}")
        server = smtplib.SMTP(
            host=self.smtp_server,
            port=self.smtp_port,
            timeout=self.timeout_seconds,
        )
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()
        return server

    def _send_message(self, msg: MIMEMultipart):
        if not self.enabled:
            print("⚠️ EMAIL_ENABLED=false - Email no se enviará")
            return False, "EMAIL_ENABLED=false"

        try:
            print(f"📧 Intentando enviar email a {msg['To']}")
            print(f"   Servidor: {self.smtp_server}:{self.smtp_port}")
            print(f"   Usuario: {self.email_user}")

            with self._open_smtp_connection() as server:
                print(f"✅ Conexión establecida")
                print(f"🔑 Autenticando...")

                server.login(self.email_user, self.email_password)
                print(f"✅ Autenticación exitosa")

                print(f"📨 Enviando mensaje...")
                server.send_message(msg)
                print(f"✅ Email enviado exitosamente a {msg['To']}")

            return True, "Email enviado exitosamente"

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Error de autenticación SMTP: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg

        except smtplib.SMTPException as e:
            error_msg = f"Error SMTP: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg

        except ssl.SSLError as e:
            error_msg = f"Error SSL: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg

        except ConnectionRefusedError as e:
            error_msg = f"Conexión rechazada: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg

        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback

            traceback.print_exc()
            return False, error_msg

    def generar_qr_code(self, codigo_reserva: str) -> BytesIO:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(codigo_reserva)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    def crear_email_html(
        self, user_name: str, codigo_reserva: str, reserva_data: dict
    ) -> str:
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confirmación de Reserva</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    border: 1px solid #ddd;
                }}
                .detail {{
                    margin: 10px 0;
                    padding: 10px;
                    background-color: white;
                    border-left: 3px solid #4CAF50;
                }}
                .qr-container {{
                    text-align: center;
                    margin: 20px 0;
                    padding: 20px;
                    background-color: white;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    padding: 10px;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔋 Chargeway</h1>
                <p>Confirmación de Reserva</p>
            </div>
            
            <div class="content">
                <h2>¡Hola, {user_name}!</h2>
                <p>Tu reserva ha sido confirmada exitosamente.</p>
                
                <div class="detail">
                    <strong>📋 Código de Reserva:</strong> {codigo_reserva}
                </div>
                
                <div class="detail">
                    <strong>📍 Estación:</strong> {reserva_data.get('estacion_nombre','N/A')}
                </div>
                
                <div class="detail">
                    <strong>🗺️ Dirección:</strong> {reserva_data.get('estacion_direccion','N/A')}
                </div>
                
                <div class="detail">
                    <strong>📅 Fecha:</strong> {reserva_data.get('fecha','N/A')}
                </div>
                
                <div class="detail">
                    <strong>🕐 Hora de inicio:</strong> {reserva_data.get('hora_inicio','N/A')}
                </div>
                
                <div class="detail">
                    <strong>⏱️ Duración:</strong> {reserva_data.get('duracion_horas','N/A')} hora(s)
                </div>
                
                <div class="qr-container">
                    <p><strong>Escanea este código QR en la estación:</strong></p>
                    <img src="cid:qr_code" alt="Código QR" style="max-width: 250px;"/>
                </div>
                
                <p style="margin-top: 20px;">
                    <strong>Instrucciones:</strong>
                </p>
                <ol>
                    <li>Llega a la estación a la hora programada</li>
                    <li>Escanea el código QR en el kiosko</li>
                    <li>Conecta tu vehículo y comienza la carga</li>
                </ol>
            </div>
            
            <div class="footer">
                <p>Si tienes alguna pregunta, contáctanos en {self.support_email}</p>
                <p>Chargeway - No te dejes de mover 🚗⚡</p>
            </div>
        </body>
        </html>
        """
        return html

    def enviar_confirmacion_reserva(
        self, destinatario_email, destinatario_nombre, reserva
    ):
        try:
            print(f"\n{'='*60}")
            print(f"📧 PREPARANDO EMAIL DE CONFIRMACIÓN")
            print(f"{'='*60}")

            codigo_reserva = getattr(
                reserva, "codigo", f"CHW-R{getattr(reserva, 'id', 0):05d}"
            )

            print(f"Destinatario: {destinatario_email}")
            print(f"Nombre: {destinatario_nombre}")
            print(f"Código reserva: {codigo_reserva}")

            reserva_data = {
                "estacion_nombre": getattr(reserva, "estacion_nombre", "N/A"),
                "estacion_direccion": getattr(reserva, "estacion_direccion", "N/A"),
                "fecha": (
                    reserva.fecha.strftime("%d/%m/%Y")
                    if getattr(reserva, "fecha", None)
                    else "N/A"
                ),
                "hora_inicio": (
                    reserva.hora_inicio.strftime("%H:%M")
                    if getattr(reserva, "hora_inicio", None)
                    else "N/A"
                ),
                "duracion_horas": getattr(reserva, "duracion_horas", "N/A"),
            }

            print(f"📋 Datos de la reserva: {reserva_data}")

            msg = MIMEMultipart("related")
            msg["Subject"] = f"✅ Reserva Confirmada - {codigo_reserva}"
            msg["From"] = formataddr((self.from_name, self.email_user))
            msg["To"] = destinatario_email

            print(f"📝 Generando HTML del email...")
            msg.attach(
                MIMEText(
                    self.crear_email_html(
                        destinatario_nombre, codigo_reserva, reserva_data
                    ),
                    "html",
                )
            )

            print(f"🔲 Generando código QR...")
            qr_image = MIMEImage(self.generar_qr_code(codigo_reserva).read())
            qr_image.add_header("Content-ID", "<qr_code>")
            msg.attach(qr_image)

            ok, mensaje = self._send_message(msg)

            print(f"{'='*60}")
            if ok:
                print(f"✅ RESULTADO: Email enviado exitosamente")
            else:
                print(f"❌ RESULTADO: Error - {mensaje}")
            print(f"{'='*60}\n")

            return ok, mensaje, codigo_reserva

        except Exception as e:
            error_msg = f"Error al enviar email: {str(e)}"
            print(f"❌ EXCEPCIÓN: {error_msg}")
            import traceback

            traceback.print_exc()
            return False, error_msg, None


def email_service_from_env() -> EmailService:
    """
    Crea una instancia de EmailService desde variables de entorno.
    """
    # ✅ MEJORA: Logging de configuración
    print(f"\n🔧 CONFIGURACIÓN DE EMAIL SERVICE")
    print(f"{'='*60}")
    print(f"SMTP_SERVER: {os.getenv('SMTP_SERVER', 'NO CONFIGURADO')}")
    print(f"SMTP_PORT: {os.getenv('SMTP_PORT', 'NO CONFIGURADO')}")
    print(f"EMAIL_USER: {os.getenv('EMAIL_USER', 'NO CONFIGURADO')}")
    print(
        f"EMAIL_PASSWORD: {'***' if os.getenv('EMAIL_PASSWORD') else 'NO CONFIGURADO'}"
    )
    print(f"EMAIL_USE_SSL: {os.getenv('EMAIL_USE_SSL', 'true')}")
    print(f"EMAIL_ENABLED: {os.getenv('EMAIL_ENABLED', 'true')}")
    print(f"EMAIL_SSL_VERIFY: {os.getenv('EMAIL_SSL_VERIFY', 'true')}")
    print(f"{'='*60}\n")

    return EmailService(
        smtp_server=os.getenv("SMTP_SERVER", ""),
        smtp_port=int(os.getenv("SMTP_PORT", 465)),
        email_user=os.getenv("EMAIL_USER", ""),
        email_password=os.getenv("EMAIL_PASSWORD", ""),
        from_name=os.getenv("EMAIL_FROM_NAME", "Chargeway"),
        use_ssl=os.getenv("EMAIL_USE_SSL", "true").lower() == "true",
        enabled=os.getenv("EMAIL_ENABLED", "true").lower() == "true",
        timeout_seconds=int(os.getenv("EMAIL_TIMEOUT_SECONDS", "12")),
        support_email=os.getenv("SUPPORT_EMAIL", "soporte@chargeway.com"),
    )
