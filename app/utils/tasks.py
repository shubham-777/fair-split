import smtplib
from email.message import EmailMessage
from typing import Optional

from app.config import settings


def send_mail(subject, body, to_emails: list, from_email: Optional[str] = None):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email if from_email else settings.DEFAULT_SENDER_EMAIL
    msg["To"] = ", ".join(to_emails)
    msg.set_content(body)
    
    smtp_server = settings.SMTP_HOST
    smtp_port = int(settings.SMTP_PORT)
    username = settings.SMTP_USERNAME
    password = settings.SMTP_PASSWORD
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        if settings.TLS_ENABLED:
            server.starttls()
        server.login(username, password)
        server.send_message(msg)

