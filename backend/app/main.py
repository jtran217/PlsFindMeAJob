from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel, ValidationError, validator
from typing import List, Optional
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

BASE_DIR = Path(__file__).resolve().parent.parent
PROFILE_PATH = BASE_DIR / "data" / "profile.json"

# Pydantic models for validation
class Basics(BaseModel):
    name: str
    email: str
    phone: str
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    
    @validator('email')
    def validate_email(cls, v):
        import re
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', v):
            raise ValueError('Please enter a valid email address')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name is required')
        return v.strip()

class Experience(BaseModel):
    company: Optional[str] = ""
    position: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    location: Optional[str] = ""
    bullets: Optional[List[str]] = []

class Education(BaseModel):
    institution: Optional[str] = ""
    location: Optional[str] = ""
    degree: Optional[str] = ""
    expected_date: Optional[str] = ""
    start_date: Optional[str] = ""
    coursework: Optional[str] = ""

class Project(BaseModel):
    name: Optional[str] = ""
    description: Optional[str] = ""

class Profile(BaseModel):
    basics: Basics
    experiences: List[Experience] = []
    education: List[Education] = []
    skills: List[str] = []
    projects: List[Project] = []
    
    @validator('skills')
    def validate_skills(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one skill is required')
        return v
    
    @validator('experiences')
    def validate_experiences(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one work experience is required')
        return v
        
    @validator('education')
    def validate_education(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one education entry is required')
        return v

# Response models
class ProfileResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Profile] = None

class SaveResponse(BaseModel):
    success: bool
    message: str
    errors: Optional[dict] = None


app = FastAPI(title="PlsFindMeAJob API")

origins = [
    "http://localhost:5173",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.get("/")
def root():
    return {"message": "PlsFindMeAJob API is running 🚀"}

@app.get("/api/jobs")
def get_jobs(skip:int = 0, limit:int = 15, db:Session = Depends(get_db)):
    total = db.query(models.Job).count()
    jobs = db.query(models.Job).offset(skip).limit(limit).all()

    return {
     "total": total,
     "data": jobs
    }

@app.get("/api/profile", response_model=Profile)
def get_profile():
    """Get user profile data with proper error handling."""
    try:
        # Ensure data directory exists
        PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if profile file exists, create empty one if not
        if not PROFILE_PATH.exists():
            empty_profile = {
                "basics": {"name": "", "email": "", "phone": "", "linkedin": "", "github": ""},
                "experiences": [],
                "education": [],
                "skills": [],
                "projects": []
            }
            with open(PROFILE_PATH, "w") as f:
                json.dump(empty_profile, f, indent=2)
            logger.info("Created new empty profile file")
        
        with open(PROFILE_PATH, "r") as f:
            profile_data = json.load(f)
        
        # Validate the loaded data
        try:
            validated_profile = Profile(**profile_data)
            return validated_profile
        except ValidationError:
            # If validation fails, return empty profile
            logger.warning("Profile validation failed, returning empty profile")
            return Profile(
                basics=Basics(name="", email="", phone=""),
                experiences=[],
                education=[],
                skills=[],
                projects=[]
            )
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile data is corrupted"
        )
    except Exception as e:
        logger.error(f"Error loading profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load profile"
        )


@app.post("/api/profile", response_model=SaveResponse)
def save_profile(profile_data: dict):
    """Save user profile with validation and proper error handling."""
    try:
        # Validate the incoming data
        try:
            validated_profile = Profile(**profile_data)
        except ValidationError as e:
            # Extract field-specific errors
            errors = {}
            for error in e.errors():
                field = '.'.join(str(loc) for loc in error['loc'])
                errors[field] = error['msg']
            
            logger.warning(f"Validation errors: {errors}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "success": False,
                    "message": "Validation failed",
                    "errors": errors
                }
            )
        
        # Ensure data directory exists
        PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the validated profile
        with open(PROFILE_PATH, "w") as f:
            json.dump(validated_profile.dict(), f, indent=2)
        
        logger.info("Profile saved successfully")
        return SaveResponse(
            success=True,
            message="Profile saved successfully!"
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions (validation errors)
        raise
    except PermissionError as e:
        logger.error(f"Permission error saving profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Permission denied: Cannot save profile"
            }
        )
    except Exception as e:
        logger.error(f"Error saving profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Failed to save profile"
            }
        )
    
