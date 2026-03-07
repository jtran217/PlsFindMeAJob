from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.services.jobs_service import JobsService
from app.api.dependencies import get_db
from app.core.exceptions import ValidationError
from app.core.config import settings
from app.services.generator_service import GeneratorService
from app.utils.file_handler import ProfileFileHandler
import logging

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter()

@router.post("/generate/resume")
def generate_resume(job_id: str = Query(...), 
                   db: Session = Depends(get_db)):
    generator = GeneratorService()
    # Initialize ProfileFileHandler with the configured profile path
    file_reader = ProfileFileHandler(settings.PROFILE_PATH)
    # Get job so we can get job_description
    job = JobsService(db).get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    # Load profile data using the ProfileFileHandler method
    profile = file_reader.load_profile_data()
    # Generate optimized resume
    result = generator.optimize_resume(job_description=job.description, profile_json=profile)
    return result
 
