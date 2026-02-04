"""
Servicio de Email para ChargeWay
Envía confirmaciones de reserva con código QR

✅ Listo para SMTP con SSL (puerto 465) o STARTTLS (puerto 587)
✅ Soporta "From Name" (nombre visible del remitente)
✅ Soporta EMAIL_ENABLED para activar/desactivar sin romper la app
✅ Timeout para evitar que se "cuelgue" la conexión
✅ VERSIÓN ADAPTADA: Usa el código de reserva ya generado (reserva.codigo)
✅ MVP: EMAIL_SSL_VERIFY=false permite evitar fallas de certificados en DEV
"""

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
    """Servicio para envío de emails de confirmación/cancelación de reservas"""

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
        """
        Inicializar servicio de email

        Args:
            smtp_server: Servidor SMTP (ej: mail.naranja.com.py)
            smtp_port: Puerto SMTP (465 para SSL, 587 para STARTTLS)
            email_user: Email desde el cual enviar
            email_password: Contraseña del email (NO hardcodear en el repo)
            from_name: Nombre visible del remitente (display name)
            use_ssl: True para SSL directo (SMTP_SSL). Normalmente True si puerto=465.
            enabled: Permite activar/desactivar envío (MVP friendly)
            timeout_seconds: Timeout para evitar bloqueos infinitos
            support_email: Email de soporte mostrado en plantillas
        """
        self.smtp_server = smtp_server
        self.smtp_port = int(smtp_port)
        self.email_user = email_user
        self.email_password = email_password

        self.from_name = from_name
        self.use_ssl = bool(use_ssl)
        self.enabled = bool(enabled)
        self.timeout_seconds = int(timeout_seconds)
        self.support_email = support_email

    # -----------------------------
    # Helpers de conexión SMTP
    # -----------------------------
    def _open_smtp_connection(self):
        """
        Abre la conexión SMTP de acuerdo al tipo de seguridad:

        - Puerto 465: SSL directo con SMTP_SSL (NO se usa starttls())
        - Puerto 587: SMTP normal + STARTTLS

        Retorna:
            Objeto SMTP conectado (context manager)
        """
        # Si el puerto es 465, forzamos SSL directo
        if self.smtp_port == 465:
            self.use_ssl = True

        if self.use_ssl:
            # SSL directo (465)
            # ---------------------------------------------------------
            # ⚠️ IMPORTANTE (MVP/HACKATÓN):
            # Algunos servidores SMTP o entornos locales no tienen la
            # cadena completa de certificados. Para no bloquear el demo,
            # permitimos desactivar la verificación con EMAIL_SSL_VERIFY=false.
            #
            # En PRODUCCIÓN: EMAIL_SSL_VERIFY debe ser true.
            # ---------------------------------------------------------
            verify_ssl = os.getenv("EMAIL_SSL_VERIFY", "true").lower() == "true"

            if verify_ssl:
                # Contexto SSL normal (verifica certificados)
                context = ssl.create_default_context()
            else:
                # Contexto SSL "inseguro": cifrado sí, verificación de certificado no
                context = ssl._create_unverified_context()

            return smtplib.SMTP_SSL(
                host=self.smtp_server,
                port=self.smtp_port,
                timeout=self.timeout_seconds,
                context=context,
            )

        # STARTTLS (típico 587)
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
        """
        Envía el mensaje SMTP (login + send_message).
        Respeta EMAIL_ENABLED para no enviar en entornos de demo.
        """
        if not self.enabled:
            # Si está deshabilitado, no enviamos y devolvemos éxito "simulado"
            return True, "EMAIL_ENABLED=false (envío deshabilitado por configuración)"

        # Abrimos conexión y enviamos
        with self._open_smtp_connection() as server:
            server.login(self.email_user, self.email_password)
            server.send_message(msg)

        return True, "Email enviado exitosamente"

    # -----------------------------
    # QR
    # -----------------------------
    def generar_qr_code(self, codigo_reserva: str) -> BytesIO:
        """
        Genera un código QR con el código de reserva

        Args:
            codigo_reserva: Código de la reserva

        Returns:
            BytesIO: Imagen QR en formato PNG
        """
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

    # -----------------------------
    # HTML templates
    # -----------------------------
    def crear_email_html(self, user_name: str, codigo_reserva: str, reserva_data: dict) -> str:
        """
        Crea el contenido HTML del email de confirmación.

        Args:
            user_name: Nombre del usuario
            codigo_reserva: Código único de la reserva
            reserva_data: Dict con datos (estacion_nombre, fecha, hora, etc)

        Returns:
            str: HTML del email
        """
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confirmación de Reserva - ChargeWay</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 0;">
                        <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; overflow: hidden; margin-top: 20px; margin-bottom: 20px;">

                            <!-- Header -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #2c5f2d 0%, #4CAF50 100%); padding: 40px 20px; text-align: center;">
                                    <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: bold;">
                                        ⚡ ChargeWay
                                    </h1>
                                    <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 16px;">
                                        Confirmación de Reserva
                                    </p>
                                </td>
                            </tr>

                            <!-- Saludo -->
                            <tr>
                                <td style="padding: 30px 40px 20px 40px;">
                                    <h2 style="margin: 0 0 10px 0; color: #333333; font-size: 24px;">
                                        ¡Hola, {user_name}! 👋
                                    </h2>
                                    <p style="margin: 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                        Tu reserva ha sido confirmada exitosamente. Aquí están los detalles:
                                    </p>
                                </td>
                            </tr>

                            <!-- Código de Reserva -->
                            <tr>
                                <td style="padding: 0 40px 30px 40px;">
                                    <div style="background: #f8f9fa; border-left: 4px solid #4CAF50; padding: 20px; border-radius: 5px;">
                                        <p style="margin: 0 0 10px 0; color: #666; font-size: 14px; font-weight: bold; text-transform: uppercase;">
                                            Código de Reserva
                                        </p>
                                        <p style="margin: 0; color: #2c5f2d; font-size: 28px; font-weight: bold; font-family: 'Courier New', monospace; letter-spacing: 2px;">
                                            {codigo_reserva}
                                        </p>
                                        <p style="margin: 10px 0 0 0; color: #999; font-size: 12px;">
                                            Guarda este código para acceder a la estación de carga
                                        </p>
                                    </div>
                                </td>
                            </tr>

                            <!-- Detalles de la Reserva -->
                            <tr>
                                <td style="padding: 0 40px 30px 40px;">
                                    <h3 style="margin: 0 0 15px 0; color: #333333; font-size: 18px;">
                                        📋 Detalles de tu Reserva
                                    </h3>
                                    <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                        <tr>
                                            <td style="padding: 10px 0; border-bottom: 1px solid #eeeeee;">
                                                <strong style="color: #666;">🔌 Estación:</strong>
                                            </td>
                                            <td style="padding: 10px 0; border-bottom: 1px solid #eeeeee; text-align: right; color: #333;">
                                                {reserva_data.get('estacion_nombre', 'N/A')}
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 10px 0; border-bottom: 1px solid #eeeeee;">
                                                <strong style="color: #666;">📍 Dirección:</strong>
                                            </td>
                                            <td style="padding: 10px 0; border-bottom: 1px solid #eeeeee; text-align: right; color: #333;">
                                                {reserva_data.get('estacion_direccion', 'N/A')}
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 10px 0; border-bottom: 1px solid #eeeeee;">
                                                <strong style="color: #666;">📅 Fecha:</strong>
                                            </td>
                                            <td style="padding: 10px 0; border-bottom: 1px solid #eeeeee; text-align: right; color: #333;">
                                                {reserva_data.get('fecha', 'N/A')}
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 10px 0; border-bottom: 1px solid #eeeeee;">
                                                <strong style="color: #666;">🕐 Hora de inicio:</strong>
                                            </td>
                                            <td style="padding: 10px 0; border-bottom: 1px solid #eeeeee; text-align: right; color: #333;">
                                                {reserva_data.get('hora_inicio', 'N/A')}
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 10px 0;">
                                                <strong style="color: #666;">⏱️ Duración:</strong>
                                            </td>
                                            <td style="padding: 10px 0; text-align: right; color: #333;">
                                                {reserva_data.get('duracion_horas', 'N/A')} hora(s)
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>

                            <!-- QR Code -->
                            <tr>
                                <td style="padding: 0 40px 30px 40px; text-align: center;">
                                    <h3 style="margin: 0 0 15px 0; color: #333333; font-size: 18px;">
                                        📱 Código QR de Acceso
                                    </h3>
                                    <p style="margin: 0 0 15px 0; color: #666; font-size: 14px;">
                                        Escanea este código en la estación para activar tu reserva
                                    </p>
                                    <img src="cid:qr_code" alt="Código QR" style="max-width: 200px; border: 2px solid #eeeeee; border-radius: 10px; padding: 10px;"/>
                                </td>
                            </tr>

                            <!-- Instrucciones -->
                            <tr>
                                <td style="padding: 0 40px 30px 40px;">
                                    <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 5px; padding: 15px;">
                                        <h4 style="margin: 0 0 10px 0; color: #856404; font-size: 16px;">
                                            ⚠️ Instrucciones Importantes
                                        </h4>
                                        <ul style="margin: 0; padding-left: 20px; color: #856404; font-size: 14px;">
                                            <li>Llega 5 minutos antes de tu hora reservada</li>
                                            <li>Ten el código de reserva o el QR listo en tu móvil</li>
                                            <li>Si necesitas cancelar, hazlo con al menos 2 horas de anticipación</li>
                                            <li>Contacta al soporte si tienes algún problema: {self.support_email}</li>
                                        </ul>
                                    </div>
                                </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                                <td style="background: #f8f9fa; padding: 30px 40px; text-align: center; border-top: 1px solid #eeeeee;">
                                    <p style="margin: 0 0 10px 0; color: #666666; font-size: 14px;">
                                        ¿Necesitas ayuda? Contáctanos
                                    </p>
                                    <p style="margin: 0 0 20px 0;">
                                        <a href="mailto:{self.support_email}" style="color: #4CAF50; text-decoration: none; font-weight: bold;">
                                            {self.support_email}
                                        </a>
                                    </p>
                                    <p style="margin: 0; color: #999999; font-size: 12px;">
                                        © 2026 ChargeWay. Todos los derechos reservados.
                                    </p>
                                    <p style="margin: 5px 0 0 0; color: #999999; font-size: 12px;">
                                        Este es un email automático, por favor no respondas directamente.
                                    </p>
                                </td>
                            </tr>

                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        return html

    # -----------------------------
    # Public API
    # -----------------------------
    def enviar_confirmacion_reserva(self, destinatario_email, destinatario_nombre, reserva):
        """
        Envía email de confirmación de reserva con código QR.
        Usa el código que YA está en reserva.codigo.

        Returns:
            tuple: (success: bool, mensaje: str, codigo_reserva: str|None)
        """
        try:
            codigo_reserva = getattr(
                reserva,
                "codigo",
                getattr(reserva, "codigo_reserva", f"CHW-R{getattr(reserva, 'id', 0):05d}"),
            )

            reserva_data = {
                "estacion_nombre": getattr(reserva, "estacion_nombre", "N/A"),
                "estacion_direccion": getattr(reserva, "estacion_direccion", "N/A"),
                "fecha": reserva.fecha.strftime("%d/%m/%Y") if getattr(reserva, "fecha", None) else "N/A",
                "hora_inicio": reserva.hora_inicio.strftime("%H:%M") if getattr(reserva, "hora_inicio", None) else "N/A",
                "duracion_horas": getattr(reserva, "duracion_horas", "N/A"),
            }

            msg = MIMEMultipart("related")
            msg["Subject"] = f"✅ Reserva Confirmada - {codigo_reserva}"
            msg["From"] = formataddr((self.from_name, self.email_user))
            msg["To"] = destinatario_email

            html_content = self.crear_email_html(destinatario_nombre, codigo_reserva, reserva_data)
            msg.attach(MIMEText(html_content, "html"))

            qr_buffer = self.generar_qr_code(codigo_reserva)
            qr_image = MIMEImage(qr_buffer.read())
            qr_image.add_header("Content-ID", "<qr_code>")
            qr_image.add_header("Content-Disposition", "inline", filename="qr.png")
            msg.attach(qr_image)

            ok, mensaje = self._send_message(msg)
            return True, mensaje, codigo_reserva

        except smtplib.SMTPAuthenticationError:
            return False, "Error de autenticación con el servidor de email. Verifica credenciales.", None
        except (smtplib.SMTPException, OSError) as e:
            return False, f"Error al enviar email: {str(e)}", None
        except Exception as e:
            return False, f"Error inesperado: {str(e)}", None

    def enviar_cancelacion_reserva(self, destinatario_email, destinatario_nombre, codigo_reserva, reserva_data):
        """
        Envía email de confirmación de cancelación.

        Returns:
            tuple: (success: bool, mensaje: str)
        """
        try:
            html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <style>body {{ font-family: Arial, sans-serif; }}</style>
            </head>
            <body style="margin: 0; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px;">
                    <h1 style="color: #d32f2f; border-bottom: 3px solid #d32f2f; padding-bottom: 10px;">
                        ⚠️ Reserva Cancelada
                    </h1>
                    <p>Hola, <strong>{destinatario_nombre}</strong></p>
                    <p>Tu reserva <strong>{codigo_reserva}</strong> ha sido cancelada exitosamente.</p>

                    <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3>Detalles de la reserva cancelada:</h3>
                        <p><strong>Estación:</strong> {reserva_data.get('estacion_nombre', 'N/A')}</p>
                        <p><strong>Fecha:</strong> {reserva_data.get('fecha', 'N/A')}</p>
                        <p><strong>Hora:</strong> {reserva_data.get('hora_inicio', 'N/A')}</p>
                    </div>

                    <p>Esperamos verte pronto en ChargeWay.</p>
                    <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                        © 2026 ChargeWay - Este es un email automático
                    </p>
                </div>
            </body>
            </html>
            """

            msg = MIMEMultipart()
            msg["Subject"] = f"❌ Reserva Cancelada - {codigo_reserva}"
            msg["From"] = formataddr((self.from_name, self.email_user))
            msg["To"] = destinatario_email
            msg.attach(MIMEText(html, "html"))

            ok, mensaje = self._send_message(msg)
            return True, mensaje

        except smtplib.SMTPAuthenticationError:
            return False, "Error de autenticación con el servidor de email. Verifica credenciales."
        except (smtplib.SMTPException, OSError) as e:
            return False, f"Error al enviar email de cancelación: {str(e)}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"


def email_service_from_env() -> EmailService:
    """
    Crea EmailService leyendo configuración desde .env / variables de entorno.

    Variables esperadas:
      SMTP_SERVER
      SMTP_PORT
      EMAIL_USER
      EMAIL_PASSWORD
      EMAIL_FROM_NAME
      EMAIL_USE_SSL
      EMAIL_ENABLED
      EMAIL_TIMEOUT_SECONDS
      SUPPORT_EMAIL
    """
    smtp_server = os.getenv("SMTP_SERVER", "")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    email_user = os.getenv("EMAIL_USER", "")
    email_password = os.getenv("EMAIL_PASSWORD", "")

    from_name = os.getenv("EMAIL_FROM_NAME", "Chargeway - no te dejes de mover")
    use_ssl = os.getenv("EMAIL_USE_SSL", "true").lower() == "true"
    enabled = os.getenv("EMAIL_ENABLED", "true").lower() == "true"
    timeout_seconds = int(os.getenv("EMAIL_TIMEOUT_SECONDS", "12"))
    support_email = os.getenv("SUPPORT_EMAIL", "soporte@chargeway.com")

    return EmailService(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        email_user=email_user,
        email_password=email_password,
        from_name=from_name,
        use_ssl=use_ssl,
        enabled=enabled,
        timeout_seconds=timeout_seconds,
        support_email=support_email,
    )
