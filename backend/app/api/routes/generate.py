from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.services.jobs_service import JobsService
from app.services.resume_service import ResumeService
from app.api.dependencies import get_db
from app.core.exceptions import ValidationError
from app.core.config import settings
from app.services.generator_service import GeneratorService
import logging

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter()

@router.post("/generate/resume")
async def generate_resume(job_id: str = Query(...), 
                   db: Session = Depends(get_db)):
    generator = GeneratorService()
    resume_service = ResumeService()
    
    # Get job so we can get job_description
    job = JobsService(db).get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Load resume data using the enhanced resume service
    resume = await resume_service.get_resume()
    
    # Generate optimized resume using the enhanced resume data
    result = generator.optimize_resume(job_description=str(job.description), profile_json=resume.dict())
    return result
 
