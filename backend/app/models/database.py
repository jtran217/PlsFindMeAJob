"""
SQLAlchemy database models for the PlsFindMeAJob application.
Contains all database table definitions and ORM models.
"""
from sqlalchemy import Column, String, Integer, Text
from app.database import Base


class Job(Base):
    """
    SQLAlchemy model for job postings.
    
    Represents job listings scraped from various job sites with comprehensive
    job details including company information, requirements, and metadata.
    """
    __tablename__ = "job_list"

    # Primary identifier
    id = Column(String, primary_key=True, index=True)

    # Source information
    site = Column(String)  # Job board source (e.g., "indeed", "linkedin")
    job_url = Column(String)  # Original job posting URL
    job_url_direct = Column(String)  # Direct application URL

    # Basic job information (indexed for search performance)
    title = Column(String, index=True)  # Job title/position
    company = Column(String, index=True)  # Company name
    location = Column(String, index=True)  # Job location

    # Temporal and classification data
    date_posted = Column(String)  # Date job was posted
    job_type = Column(String)  # Full-time, part-time, contract, etc.
    is_remote = Column(Integer)  # 0 or 1 (boolean stored as integer)

    # Detailed content
    description = Column(Text)  # Full job description

    # Company information
    company_url = Column(String)  # Company website
    company_url_direct = Column(String)  # Direct company page

    # Requirements and qualifications
    skills = Column(Text)  # Required skills (comma-separated or JSON)
    experience_range = Column(String)  # Experience level required

    # Application tracking
    status = Column(String)  # Application status: ready, applied, rejected, etc.