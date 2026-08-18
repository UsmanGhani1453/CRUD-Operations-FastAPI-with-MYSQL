import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core import config

logger = logging.getLogger(__name__)


def send_verification_email(receiver_email: str, token: str) -> None:
    """
    Send an account-verification email.

    Credentials are read from environment variables (SENDER_EMAIL,
    SENDER_PASSWORD) - never hardcode them in source. If they aren't
    configured, this logs a warning instead of crashing the background
    task (create_user already succeeded; email is a secondary effect).
    """
    if not config.SENDER_EMAIL or not config.SENDER_PASSWORD:
        logger.warning(
            "SENDER_EMAIL / SENDER_PASSWORD not configured - "
            "skipping verification email to %s",
            receiver_email,
        )
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify Your HAAK Account"
    message["From"] = config.SENDER_EMAIL
    message["To"] = receiver_email

    verify_url = f"{config.APP_BASE_URL}/users/verify?token={token}"

    html = f"""
    <html>
      <body>
        <h2>Welcome to HAAK!</h2>
        <p>You are one step away from completing your account registration.</p>
        <p>Please click the link below to verify your email address:</p>
        <a href="{verify_url}" style="padding: 10px 20px; background-color: #000; color: #fff; text-decoration: none;">Verify My Account</a>
      </body>
    </html>
    """
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
            server.sendmail(config.SENDER_EMAIL, receiver_email, message.as_string())
    except smtplib.SMTPException:
        logger.exception("Failed to send verification email to %s", receiver_email)
