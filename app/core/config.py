from enum import Enum
from functools import lru_cache
from typing import Optional, Union

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    local = "local"
    uat = "uat"
    test = "test"
    prod = "prod"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, Environment):
            return self.value == other.value
        return self.value == other


class Settings(BaseSettings):
    APP_NAME: str = "Risevale Tour API"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    BASE_API_URL: str = "http://localhost:8000"
    COMPANY_NAME: str = "Risevale Tours"
    COMPANY_EMAIL: str = "info@risevale.com"
    COMPANY_PHONE: str = "+254-XXX-XXX-XXX"
    COMPANY_ADDRESS: str = "Nairobi, Kenya"
    COMPANY_WEBSITE: str = "https://risevale.com"

    # Environment
    ENVIRONMENT: Environment = Environment.local
    TIME_ZONE: str = "Africa/Nairobi"
    DATABASE_URI: Optional[Union[PostgresDsn, str]] = "sqlite:///./test.db"

    # Security & Authentication
    ACCESS_TOKEN_EXP_MINUTES: int = 7 * 24 * 60
    REFRESH_TOKEN_EXP_DAYS: int = 30
    PASSWORD_RESET_TOKEN_EXP_HOURS: int = 1

    # Test User Credentials
    TEST_USER_EMAIL: str = "test@risevale.com"
    TEST_USER_PASSWORD: str = "@pass_123"

    # Redis Configuration
    REDIS_HOST: Optional[str] = None
    REDIS_DB: int = 0

    # Email Configuration
    EMAIL_SMTP_SERVER: str = "smtp.gmail.com"
    EMAIL_SMTP_PORT: int = 587
    EMAIL_SENDER: str = "noreply@risevale.com"
    EMAIL_SENDER_PASSWORD: str = ""
    ADMIN_EMAIL: str = "admin@risevale.com"
    GCP_PRIVATE_BUCKET: str
    GCP_PUBLIC_BUCKET: str
    MEDIA_BASE: str = "media"

    model_config = SettingsConfigDict(
        extra="allow", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


__all__ = ["get_settings", "Settings", "Environment"]
