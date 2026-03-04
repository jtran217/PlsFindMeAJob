"""
Configuration management for the PlsFindMeAJob application.
Centralizes all configuration settings and paths.
"""
from pathlib import Path
from typing import List
import logging

class Settings:
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
    
    def __post_init__(self):
        """Configure logging after initialization."""
        logging.basicConfig(level=getattr(logging, self.LOG_LEVEL))


# Global settings instance
settings = Settings()

# Configure logging
logger = logging.getLogger(__name__)