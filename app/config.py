"""
Application configuration using Pydantic Settings
"""
import os
from typing import Optional

from pydantic import computed_field, PostgresDsn
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    class Config:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_file = os.path.join(base_dir, ".env")
        case_sensitive = True
    
    # App
    APP_NAME: str = "FairSplit API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DB_USERNAME: str = 'postgres'
    DB_PASSWORD: str = 'shub777ham'
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_NAME: str = 'fair_split'
    
    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return f'postgresql+psycopg2://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RESET_TOKEN_EXPIRE_MINUTES: int = 10
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["*"]
    
    # AWS S3 / Cloudinary
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    #SMTP
    DEFAULT_SENDER_EMAIL: str = "notification@fairsplit.com"
    SMTP_HOST: str = "localhost"
    SMTP_PORT: str = "2525"
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    TLS_ENABLED: bool = False
    
    #Frontend Domain
    FRONTEND_DOMAIN: str = "http://localhost:8000"
    
    #Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0


settings = Settings()