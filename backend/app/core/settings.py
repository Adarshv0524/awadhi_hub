# app/core/settings.py
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env in project root if present

class Settings:
    # DB
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "awadhi_db")

    # App
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_DEBUG: bool = os.getenv("APP_DEBUG", "false").lower() in ("1","true","yes")

    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "replace-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRES_SECONDS: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_SECONDS", "900"))
    JWT_REFRESH_TOKEN_EXPIRES_SECONDS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_SECONDS", "1209600"))
    PASSWORD_RESET_TOKEN_EXPIRES_SECONDS: int = int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRES_SECONDS", "3600"))

    # Frontend URL (used in transactional email links)
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "https://awadhi.new")

    # Email (SMTP)
    SMTP_ENABLED: bool = os.getenv("SMTP_ENABLED", "false").lower() in ("1", "true", "yes")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")
    SMTP_USE_SSL: bool = os.getenv("SMTP_USE_SSL", "false").lower() in ("1", "true", "yes")
    SMTP_TIMEOUT_SECONDS: int = int(os.getenv("SMTP_TIMEOUT_SECONDS", "20"))

    # OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/oauth/google/callback")

    @property
    def mysql_url(self) -> str:
        # Use pymysql driver
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"

settings = Settings()
