"""
FastAPI dependencies for the PlsFindMeAJob application.
Provides reusable dependency injection functions.
"""
from typing import Generator
from sqlalchemy.orm import Session
from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Note:
        Automatically handles session cleanup in finally block.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()