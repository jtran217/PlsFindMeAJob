"""
Configuration management for the PlsFindMeAJob application.
Centralizes all configuration settings and paths.
"""
from pathlib import Path
from typing import List
import logging
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Base directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    
    # Profile configuration
    PROFILE_PATH: Path = DATA_DIR / "profile.json"
    
    # Database configuration
    DATABASE_URL: str = "sqlite:///./app/jobs.db"
    
    # CORS configuration
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    
    # API configuration
    API_TITLE: str = "PlsFindMeAJob API"
    API_VERSION: str = "1.0.0"
    
    # Logging configuration
    LOG_LEVEL: str = "INFO"
    
    # OpenRouter AI settings
    openrouter_api_key: str = Field(..., alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")
    openrouter_model: str = Field(default="openrouter/free", alias="OPENROUTER_MODEL")
    openrouter_max_tokens: int = Field(default=4096, alias="OPENROUTER_MAX_TOKENS")
    openrouter_timeout: int = Field(default=30, alias="OPENROUTER_TIMEOUT")

    # RxResu.me settings (optional for now since we're testing OpenRouter first)
    rxresume_api_key: str = Field(default="", alias="RXRESUME_API_KEY")
    rxresume_base_url: str = Field(default="https://rxresu.me/api/openapi", alias="RXRESUME_BASE_URL")
    rxresume_default_template: str = Field(default="azurill", alias="RXRESUME_DEFAULT_TEMPLATE")

    model_config = {"env_file": "../.env"}

    def __init__(self, **kwargs):
        """Initialize settings and configure logging."""
        super().__init__(**kwargs)
        logging.basicConfig(level=getattr(logging, self.LOG_LEVEL))


# Global settings instance
settings = Settings()

# Configure logging
logger = logging.getLogger(__name__)
