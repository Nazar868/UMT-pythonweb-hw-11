from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from src.conf.config import settings
from src.services.auth import auth_service

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str) -> None:
    """
    Генерує токен підтвердження email та надсилає лист із
    посиланням на маршрут /api/auth/confirmed_email/{token}.
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})

        message = MessageSchema(
            subject="Підтвердження електронної пошти",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_verification.html")
    except Exception as err:  # pragma: no cover
        # Не валимо реєстрацію, якщо поштовий сервер недоступний —
        # просто логуємо помилку.
        print(f"Помилка надсилання листа підтвердження: {err}")
