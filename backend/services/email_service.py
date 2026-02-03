"""
Servicio de Email para ChargeWay
Envía confirmaciones de reserva con código QR
VERSIÓN ADAPTADA: Usa el código de reserva ya generado en reservas_bp.py
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
import qrcode
from io import BytesIO


class EmailService:
    """Servicio para envío de emails de confirmación de reservas"""

    def __init__(self, smtp_server, smtp_port, email_user, email_password):
        """
        Inicializar servicio de email

        Args:
            smtp_server: Servidor SMTP (ej: smtp.gmail.com)
            smtp_port: Puerto SMTP (ej: 587)
            email_user: Email desde el cual enviar
            email_password: Contraseña del email o App Password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_user = email_user
        self.email_password = email_password

    def generar_qr_code(self, codigo_reserva):
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
        
        # Convertir a bytes
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        return buffer

    def crear_email_html(self, user_name, codigo_reserva, reserva_data):
        """
        Crea el contenido HTML del email de confirmación

        Args:
            user_name: Nombre del usuario
            codigo_reserva: Código único de la reserva (YA GENERADO)
            reserva_data: Dict con datos de la reserva (estacion_nombre, fecha, hora, etc)

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
                                            <li>Contacta al soporte si tienes algún problema: soporte@chargeway.com</li>
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
                                        <a href="mailto:soporte@chargeway.com" style="color: #4CAF50; text-decoration: none; font-weight: bold;">
                                            soporte@chargeway.com
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

    def enviar_confirmacion_reserva(self, destinatario_email, destinatario_nombre, reserva):
        """
        Envía email de confirmación de reserva con código QR
        NOTA: Usa el código que YA está en reserva.codigo

        Args:
            destinatario_email: Email del usuario
            destinatario_nombre: Nombre del usuario
            reserva: Objeto Reserva (debe tener campo .codigo)

        Returns:
            tuple: (success: bool, mensaje: str, codigo_reserva: str)
        """
        try:
            # Usar el código que ya viene en la reserva (no generar uno nuevo)
            # Si la reserva tiene un atributo 'codigo', usarlo
            # Si no, intentar con 'codigo_reserva' (compatibilidad)
            codigo_reserva = getattr(reserva, 'codigo', getattr(reserva, 'codigo_reserva', f'CHW-R{reserva.id:05d}'))

            # Preparar datos de la reserva
            reserva_data = {
                'estacion_nombre': reserva.estacion_nombre,
                'estacion_direccion': reserva.estacion_direccion,
                'fecha': reserva.fecha.strftime('%d/%m/%Y'),
                'hora_inicio': reserva.hora_inicio.strftime('%H:%M'),
                'duracion_horas': reserva.duracion_horas
            }

            # Crear mensaje
            msg = MIMEMultipart('related')
            msg['Subject'] = f'✅ Reserva Confirmada - {codigo_reserva}'
            msg['From'] = self.email_user
            msg['To'] = destinatario_email

            # Crear HTML
            html_content = self.crear_email_html(
                destinatario_nombre,
                codigo_reserva,
                reserva_data
            )

            # Adjuntar HTML
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Generar y adjuntar QR Code
            qr_buffer = self.generar_qr_code(codigo_reserva)
            qr_image = MIMEImage(qr_buffer.read())
            qr_image.add_header('Content-ID', '<qr_code>')
            msg.attach(qr_image)

            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)

            return True, "Email enviado exitosamente", codigo_reserva

        except smtplib.SMTPAuthenticationError:
            return False, "Error de autenticación con el servidor de email. Verifica las credenciales.", None
        except smtplib.SMTPException as e:
            return False, f"Error al enviar email: {str(e)}", None
        except Exception as e:
            return False, f"Error inesperado: {str(e)}", None

    def enviar_cancelacion_reserva(self, destinatario_email, destinatario_nombre, codigo_reserva, reserva_data):
        """
        Envía email de confirmación de cancelación

        Args:
            destinatario_email: Email del usuario
            destinatario_nombre: Nombre del usuario
            codigo_reserva: Código de la reserva cancelada
            reserva_data: Dict con datos de la reserva

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
            msg['Subject'] = f'❌ Reserva Cancelada - {codigo_reserva}'
            msg['From'] = self.email_user
            msg['To'] = destinatario_email
            msg.attach(MIMEText(html, 'html'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)

            return True, "Email de cancelación enviado exitosamente"

        except Exception as e:
            return False, f"Error al enviar email de cancelación: {str(e)}"