from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.services.jobs_service import JobsService
from app.api.dependencies import get_db
from app.core.exceptions import ValidationError
from app.services.generator_service import GeneratorService
import logging

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter()

@router.post("/generate/resume")
def generate_resume(job_id:str = Query(...), 
                    db:Session = Depends(get_db)
):
    generator = GeneratorService()
    job = JobsService(db).get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    # For testing, just return the job as JSON
    return {"job": job}



 
