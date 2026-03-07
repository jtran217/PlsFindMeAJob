"""
Models package for the PlsFindMeAJob application.
Provides unified access to database models.
"""

# Database models (SQLAlchemy)
from .database import Job

# Import Base for database operations
from app.database import Base

# Export all models for easy importing
__all__ = [
    # Database models
    "Job",
    "Base",
]