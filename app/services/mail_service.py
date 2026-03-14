from fastapi_mail import FastMail, MessageSchema, MessageType
from app.config.email_config import mail_config
import secrets
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)

# FastAPI-Mail is async — email sending should never block requests

async def send_mail(to :str , otp : str):
    message = MessageSchema(
        subject="Your password reset OTP",
        recipients=[to],
        body=f"""
            Your OTP for password reset is: {otp}

            This OTP expires in 10 minutes.
            Do not share this with anyone.
            """,
        subtype=MessageType.plain,
    )

    fm = FastMail(mail_config)
    try:
        await fm.send_message(message)
    except Exception as e:
        logger.error("Error sending email: %s", e)

def generate_otp():
    return secrets.randbelow(1000000)

def generate_otp_expiry_time():
    return datetime.now(timezone.utc) + timedelta(minutes=10)