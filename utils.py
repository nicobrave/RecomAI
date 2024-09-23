import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(ito_email, subject, body):
    smtp_server = "smtp-nicobrave.alwaysdata.net"  # Servidor SMTP
    smtp_port = 587  # Puerto para TLS (o 465 si usas SSL)
    smtp_user = "info@recomai.cl"  # Tu cuenta de correo
    smtp_password = "recomai2024"  # Tu contraseña

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = ito_email

    try:
        # Conexión al servidor SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Usa TLS
        server.login(smtp_user, smtp_password)  # Autenticación
        server.sendmail(smtp_user, [ito_email], msg.as_string())  # Enviar el correo
        server.quit()
        print("Correo enviado correctamente")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
