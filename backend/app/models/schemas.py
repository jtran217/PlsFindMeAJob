"""
Pydantic schemas for request/response validation and serialization.
Contains all data models used for API input/output validation.
"""
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
import re


class Basics(BaseModel):
    """Basic profile information schema."""
    name: str
    email: str
    phone: str
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format using regex."""
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', v):
            raise ValueError('Please enter a valid email address')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name is not empty."""
        if not v.strip():
            raise ValueError('Name is required')
        return v.strip()


class Experience(BaseModel):
    """Work experience schema."""
    company: Optional[str] = ""
    position: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    location: Optional[str] = ""
    bullets: Optional[List[str]] = []


class Education(BaseModel):
    """Education background schema."""
    institution: Optional[str] = ""
    location: Optional[str] = ""
    degree: Optional[str] = ""
    expected_date: Optional[str] = ""
    start_date: Optional[str] = ""
    coursework: Optional[str] = ""


class Project(BaseModel):
    """Personal/professional project schema."""
    name: Optional[str] = ""
    description: Optional[str] = ""


class Profile(BaseModel):
    """Complete user profile schema with validation."""
    basics: Basics
    experiences: List[Experience] = []
    education: List[Education] = []
    skills: List[str] = []
    projects: List[Project] = []
    
    @validator('skills')
    def validate_skills(cls, v):
        """Ensure at least one skill is provided."""
        if not v or len(v) == 0:
            raise ValueError('At least one skill is required')
        return v
    
    @validator('experiences')
    def validate_experiences(cls, v):
        """Ensure at least one work experience is provided."""
        if not v or len(v) == 0:
            raise ValueError('At least one work experience is required')
        return v
        
    @validator('education')
    def validate_education(cls, v):
        """Ensure at least one education entry is provided."""
        if not v or len(v) == 0:
            raise ValueError('At least one education entry is required')
        return v


# Response schemas
class ProfileResponse(BaseModel):
    """Response schema for profile operations."""
    success: bool
    message: str
    data: Optional[Profile] = None


class SaveResponse(BaseModel):
    """Response schema for save operations."""
    success: bool
    message: str
    errors: Optional[Dict[str, Any]] = None