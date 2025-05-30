from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Application Settings
    app_name: str = "FastAPI Authentication Service"
    environment: str = "development"
    debug: bool = False
    secret_key: str = "your-secret-key-change-in-production"
    
    # Auth0 Configuration (optional for basic setup)
    auth0_domain: Optional[str] = None
    auth0_client_id: Optional[str] = None
    auth0_client_secret: Optional[str] = None
    auth0_audience: Optional[str] = None
    
    # JWT Configuration
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Optional Services
    redis_url: Optional[str] = None
    database_url: Optional[str] = None
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Create settings instance
settings = Settings()