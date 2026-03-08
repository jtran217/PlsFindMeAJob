"""
SQLAlchemy database models for the PlsFindMeAJob application.
Contains all database table definitions and ORM models.
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


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


class ResumeJob(Base):
    """
    SQLAlchemy model for linking job applications to their customized resumes on RxResume.
    
    This table maintains the association between specific job postings and the 
    corresponding resumes created on RxResume, enabling job-specific resume
    customization and tracking.
    """
    __tablename__ = "resume_jobs"
    
    # Primary identifier
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to job posting
    job_id = Column(String, ForeignKey("job_list.id"), nullable=False, index=True)
    
    # RxResume integration fields
    rxresume_id = Column(String, nullable=False, unique=True, index=True)  # UUID from RxResume API
    resume_name = Column(String, nullable=False)  # Human-readable name like "Resume - Software Engineer at Google"
    
    # Timestamps
    created_at = Column(String, nullable=False)  # ISO timestamp when resume was created
    updated_at = Column(String, nullable=False)  # ISO timestamp of last sync
    
    # Sync status tracking
    sync_status = Column(String, default="synced")  # synced|pending|failed|error
    
    # Template configuration
    template = Column(String, default="azurill")  # RxResume template used
    user_template_override = Column(String, nullable=True)  # Manual template selection override
    
    # Relationship to job (will be added to Job model separately if needed)
    # job = relationship("Job", back_populates="resume")