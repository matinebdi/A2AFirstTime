"""Configuration for VacanceAI Backend"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # App
    app_name: str = "VacanceAI"
    debug: bool = True
    log_level: str = "INFO"
    environment: str = "development"

    # Oracle Database
    oracle_host: str = "localhost"
    oracle_port: int = 1521
    oracle_service: str = "XE"
    oracle_user: str = "VACANCEAI"
    oracle_password: str = "vacanceai"

    # JWT Auth
    jwt_secret_key: str = "vacanceai-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # Google AI (Gemini)
    google_api_key: str = ""

    # LangSmith
    langchain_tracing_v2: str = "false"
    langchain_api_key: str = ""
    langchain_project: str = "VacanceAI"
    langchain_endpoint: str = "https://api.smith.langchain.com"

    # Frontend URL
    frontend_url: str = "http://localhost:5173"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
