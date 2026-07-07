from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Всі конфіденційні дані (секретний ключ, паролі, ключі Cloudinary тощо)
    беруться ВИКЛЮЧНО зі змінних середовища (.env). У коді немає
    захардкоджених значень.
    """

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/contacts_db"

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    email_token_expire_hours: int = 24

    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = "example@meta.ua"
    mail_port: int = 465
    mail_server: str = "smtp.meta.ua"
    mail_from_name: str = "Contacts API"

    cloudinary_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    app_host: str = "0.0.0.0"
    app_port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
