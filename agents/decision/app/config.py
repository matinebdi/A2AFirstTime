"""Configuration for Decision Agent"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Agent Identity
    agent_name: str = os.getenv("AGENT_NAME", "decision")

    # Redis Configuration
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    redis_password: str = os.getenv("REDIS_PASSWORD", "")
    redis_db: int = int(os.getenv("REDIS_DB", 0))

    # Oracle Database Configuration
    oracle_user: str = os.getenv("ORACLE_USER", "SYS")
    oracle_password: str = os.getenv("ORACLE_PASSWORD", "admin")
    oracle_host: str = os.getenv("ORACLE_HOST", "localhost")
    oracle_port: int = int(os.getenv("ORACLE_PORT", 1521))
    oracle_service: str = os.getenv("ORACLE_SERVICE", "XEPDB1")
    oracle_role: str = os.getenv("ORACLE_ROLE", "SYSDBA")

    # A2A Protocol Settings
    a2a_channel_prefix: str = os.getenv("A2A_CHANNEL_PREFIX", "agent")
    a2a_message_ttl: int = int(os.getenv("A2A_MESSAGE_TTL", 3600))
    a2a_max_retries: int = int(os.getenv("A2A_MAX_RETRIES", 3))

    # AI Configuration
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")

    # Application Settings
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    environment: str = os.getenv("ENVIRONMENT", "development")

    class Config:
        env_file = ".env"


settings = Settings()
