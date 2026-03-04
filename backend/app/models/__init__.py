"""
Models package for the PlsFindMeAJob application.
Provides unified access to both database models and request/response schemas.
"""

# Database models (SQLAlchemy)
from .database import Job

# Request/Response schemas (Pydantic)
from .schemas import (
    Basics,
    Experience,
    Education,
    Project,
    Profile,
    ProfileResponse,
    SaveResponse,
)

# Import Base for database operations
from app.database import Base

# Export all models for easy importing
__all__ = [
    # Database models
    "Job",
    "Base",
    
    # Pydantic schemas
    "Basics",
    "Experience", 
    "Education",
    "Project",
    "Profile",
    "ProfileResponse",
    "SaveResponse",
]