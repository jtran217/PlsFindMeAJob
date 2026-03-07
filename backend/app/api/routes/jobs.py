"""
Jobs API routes for the PlsFindMeAJob application.

This module contains all job-related API endpoints using the router pattern.
All business logic is delegated to the JobsService class.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.services.jobs_service import JobsService
from app.api.dependencies import get_db
from app.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter()


@router.get("/jobs")
def get_jobs(
    skip: int = Query(0, ge=0, description="Number of jobs to skip for pagination"),
    limit: int = Query(15, ge=1, le=100, description="Maximum number of jobs to return"),
    search: Optional[str] = Query(None, description="Search term for job title or company"),
    status: Optional[str] = Query(None, description="Filter jobs by application status"),
    db: Session = Depends(get_db)
):
    """
    Get paginated job listings with optional search and status filtering.
    
    Args:
        skip: Number of jobs to skip for pagination (default: 0)
        limit: Maximum number of jobs to return (default: 15, max: 100)
        search: Optional search term for filtering jobs by title or company
        status: Optional status filter ('ready', 'applied', 'all', etc.)
        db: Database session (injected)
        
    Returns:
        Dictionary containing total count and job data
        
    Raises:
        HTTPException: If validation fails or database error occurs
    """
    try:
        # Create jobs service instance
        jobs_service = JobsService(db)
        
        # Handle search vs. regular pagination
        if search:
            result = jobs_service.search_jobs(search, skip, limit)
            logger.info(f"Search request: '{search}' returned {len(result['data'])} jobs")
        else:
            result = jobs_service.get_jobs_paginated(skip, limit, status)
            logger.info(f"Pagination request: skip={skip}, limit={limit}, status={status} returned {len(result['data'])} jobs")
        
        return result
        
    except ValidationError as e:
        logger.warning(f"Validation error in get_jobs: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_jobs: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An internal error occurred while retrieving jobs"
        )


@router.get("/jobs/count/status")
def get_jobs_count_by_status(db: Session = Depends(get_db)):
    """
    Get the count of jobs grouped by application status.
    
    Args:
        db: Database session (injected)
        
    Returns:
        Dictionary containing counts per status
        
    Raises:
        HTTPException: If database error occurs
    """
    try:
        jobs_service = JobsService(db)
        counts = jobs_service.get_jobs_count_by_status()
        
        return counts
        
    except ValidationError as e:
        logger.warning(f"Validation error in get_jobs_count_by_status: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_jobs_count_by_status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while counting jobs by status"
        )


@router.get("/jobs/count")
def get_jobs_count(db: Session = Depends(get_db)):
    """
    Get the total number of jobs in the database.
    
    Args:
        db: Database session (injected)
        
    Returns:
        Dictionary containing the total count
        
    Raises:
        HTTPException: If database error occurs
    """
    try:
        jobs_service = JobsService(db)
        count = jobs_service.get_jobs_count()
        
        return {"total": count}
        
    except ValidationError as e:
        logger.warning(f"Validation error in get_jobs_count: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_jobs_count: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while counting jobs"
        )


@router.get("/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    """
    Get a specific job by ID.
    
    Args:
        job_id: The ID of the job to retrieve
        db: Database session (injected)
        
    Returns:
        Job object if found
        
    Raises:
        HTTPException: If job is not found or validation fails
    """
    try:
        jobs_service = JobsService(db)
        job = jobs_service.get_job_by_id(job_id)
        
        logger.info(f"Retrieved job {job_id}: {job.title} at {job.company}")
        return job
        
    except ValidationError as e:
        logger.warning(f"Validation error in get_job: {str(e)}")
        raise HTTPException(status_code=404 if "not found" in str(e).lower() else 400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_job: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while retrieving the job"
        )