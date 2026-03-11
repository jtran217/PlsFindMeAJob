"""
PlsFindMeAJob FastAPI Application.

Main application entry point providing REST API endpoints for:
- Job management (existing functionality) 
- Resume optimization and scoring system
- Job-specific resume analysis and ranking
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Generator, List

from dotenv import load_dotenv

# Load environment variables from project root .env before any service imports
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent.parent / ".env")

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal, engine, Base
from app.job_models import Job
from app.models.resume import Resume, JobAnalysisResult, OptimizedContent, OptimizedResume
from app.services.resume_service import ResumeService  
from app.services.scoring_service import ScoringService
from app.services.optimization_service import OptimizationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="PlsFindMeAJob API",
    description="Job application management and resume optimization platform",
    version="1.0.0"
)

# CORS configuration
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5175",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection functions

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    
    Yields:
        SQLAlchemy session for database operations
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_resume_service() -> ResumeService:
    """
    Resume service dependency injection.
    
    Returns:
        Configured ResumeService instance
    """
    return ResumeService()


def get_scoring_service(db: Session = Depends(get_db)) -> ScoringService:
    """
    Scoring service dependency injection.
    
    Args:
        db: Database session dependency
        
    Returns:
        Configured ScoringService instance
    """
    return ScoringService(db)


def get_optimization_service() -> OptimizationService:
    """
    Optimization service dependency injection.

    Returns:
        Configured OptimizationService instance

    Raises:
        HTTPException: If OPENROUTER_API_KEY is not configured
    """
    try:
        return OptimizationService()
    except EnvironmentError as e:
        logger.error(f"OptimizationService configuration error: {e}")
        raise HTTPException(
            status_code=500,
            detail="AI optimization service is not configured. OPENROUTER_API_KEY is missing."
        )


# API Endpoints

@app.get("/")
def root() -> Dict[str, str]:
    """Root endpoint - API health check."""
    return {"message": "PlsFindMeAJob API is running"}


@app.get("/api/jobs")
def get_jobs(db: Session = Depends(get_db)):
    """
    Get all available jobs.
    
    Returns:
        List of all jobs from database
        
    Raises:
        HTTPException: If database query fails
    """
    try:
        jobs = db.query(Job).all()
        logger.info(f"Retrieved {len(jobs)} jobs")
        return jobs
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving jobs: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve jobs from database"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving jobs: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error"
        )

# Resume Management Endpoints

@app.get("/api/resume", response_model=Resume)
async def get_resume(resume_service: ResumeService = Depends(get_resume_service)):
    """
    Get master resume data.
    
    Returns empty resume structure if no resume exists.
    
    Returns:
        Resume object with all experiences, projects, and metadata
        
    Raises:
        HTTPException: If resume loading fails
    """
    try:
        resume = resume_service.load_master_resume()
        logger.info("Master resume retrieved successfully")
        return resume
    except Exception as e:
        logger.error(f"Failed to load master resume: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to load resume data"
        )


@app.post("/api/resume")
async def save_resume(
    resume_data: Resume, 
    resume_service: ResumeService = Depends(get_resume_service)
):
    """
    Save or update master resume data.
    
    Args:
        resume_data: Complete resume data to save
        
    Returns:
        Success confirmation message
        
    Raises:
        HTTPException: If save operation fails
    """
    try:
        success = resume_service.save_master_resume(resume_data)
        if success:
            logger.info("Master resume saved successfully")
            return {"success": True, "message": "Resume saved successfully"}
        else:
            logger.error("Resume save operation returned false")
            raise HTTPException(status_code=500, detail="Failed to save resume")
    except Exception as e:
        logger.error(f"Error saving resume: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to save resume data"
        )

@app.put("/api/resume")
async def update_resume(
    resume_data: Resume,
    resume_service: ResumeService = Depends(get_resume_service)
):
    """
    Update master resume data.

    Accepts a complete Resume object and overwrites the stored master resume.
    Semantically equivalent to POST but signals an update/replace operation.

    Args:
        resume_data: Updated resume data

    Returns:
        Success confirmation message

    Raises:
        HTTPException: If update operation fails
    """
    try:
        success = resume_service.save_master_resume(resume_data)
        if success:
            logger.info("Master resume updated successfully")
            return {"success": True, "message": "Resume updated successfully"}
        else:
            logger.error("Resume update operation returned false")
            raise HTTPException(status_code=500, detail="Failed to update resume")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating resume: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update resume data"
        )


class OptimizeResumeRequest(BaseModel):
    """Request body for resume optimization endpoint."""
    selected_experiences: List[str]
    selected_projects: List[str]


@app.post("/api/resume/optimize/{job_id}", response_model=OptimizedContent)
async def optimize_resume_for_job(
    job_id: str,
    request: OptimizeResumeRequest,
    resume_service: ResumeService = Depends(get_resume_service),
    scoring_service: ScoringService = Depends(get_scoring_service),
    optimization_service: OptimizationService = Depends(get_optimization_service),
):
    """
    Optimize selected resume items for a specific job using AI.

    Loads the master resume and the target job, filters down to the selected
    experiences and projects, then sends each item's bullet points to
    OpenRouter in a single concurrent batch call per item. Results are saved
    as a resume version and returned for user review and editing.

    Uses per-item batching strategy: one API call per selected experience or
    project (~5 calls for a typical selection vs. ~18 for per-bullet),
    costing approximately $0.010 per optimization run with claude-3.5-haiku.

    On API failure for any individual item, that item falls back to its
    original bullet text so the user always receives a complete response.

    Args:
        job_id: Unique identifier for target job
        request: Selected experience and project IDs to optimize

    Returns:
        OptimizedContent with AI-enhanced bullet points for review

    Raises:
        HTTPException: 404 if job not found, 500 if optimization fails
    """
    try:
        logger.info(
            f"Optimization requested for job {job_id} — "
            f"{len(request.selected_experiences)} experiences, "
            f"{len(request.selected_projects)} projects"
        )

        # Load master resume
        resume = resume_service.load_master_resume()

        # Fetch job from DB for description, title, company
        job_analysis = scoring_service.extract_job_requirements(job_id)
        job = scoring_service.db.query(Job).filter(Job.id == job_id).first()
        job_description = str(job.description or "") if job else ""

        # Filter resume items to only the selected IDs
        exp_id_set = set(request.selected_experiences)
        proj_id_set = set(request.selected_projects)

        selected_experiences = [
            exp for exp in resume.experiences if exp.id in exp_id_set
        ]
        selected_projects = [
            proj for proj in resume.projects if proj.id in proj_id_set
        ]

        if not selected_experiences and not selected_projects:
            raise HTTPException(
                status_code=400,
                detail="None of the provided experience or project IDs were found in the master resume."
            )

        # Run optimization (per-item batching, concurrent)
        optimized_content = await optimization_service.optimize_resume_items(
            selected_experiences=selected_experiences,
            selected_projects=selected_projects,
            job_description=job_description,
            job_title=job_analysis.job_title,
            company=job_analysis.company,
        )

        # Persist as a resume version
        resume_version = OptimizedResume(
            job_id=job_id,
            generated_at="",  # resume_service stamps this on save
            selected_experiences=request.selected_experiences,
            selected_projects=request.selected_projects,
            optimized_content=optimized_content,
        )
        resume_service.save_resume_version(job_id, resume_version)

        logger.info(f"Optimization complete and saved for job {job_id}")
        return optimized_content

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Job not found during optimization: {job_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Optimization failed for job {job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Resume optimization failed. Please try again."
        )


@app.post("/api/resume/generate-pdf/{job_id}")
async def generate_resume_pdf(
    job_id: str,
    finalized_content: OptimizedContent,
):
    """
    Generate a LaTeX PDF resume for a specific job.

    Combines the master resume data with finalized optimized content
    and compiles a professional PDF using a LaTeX template.

    Args:
        job_id: Unique identifier for target job
        finalized_content: Reviewed and approved optimized bullet points

    Returns:
        File path or download URL for the generated PDF

    Raises:
        HTTPException: 501 until PDFService is implemented in Phase 1.5
    """
    logger.info(f"PDF generation requested for job {job_id}")
    raise HTTPException(
        status_code=501,
        detail="PDF generation is not yet implemented. PDFService will be added in Phase 1.5."
    )


@app.post("/api/resume/analyze/{job_id}", response_model=JobAnalysisResult)
async def analyze_job_for_resume(
    job_id: str,
    resume_service: ResumeService = Depends(get_resume_service),
    scoring_service: ScoringService = Depends(get_scoring_service)
):
    """
    Analyze job requirements and rank resume items by relevance.
    
    Extracts keywords and technologies from job posting, then scores
    and ranks all resume experiences and projects.
    
    Args:
        job_id: Unique identifier for job to analyze
        
    Returns:
        JobAnalysisResult with job analysis and ranked resume items
        
    Raises:
        HTTPException: If job not found (404) or analysis fails (500)
    """
    try:
        logger.info(f"Starting job analysis for job_id: {job_id}")
        
        # Load master resume
        resume = resume_service.load_master_resume()
        
        # Extract job requirements
        job_analysis = scoring_service.extract_job_requirements(job_id)
        
        # Score and rank resume items
        ranked_experiences, ranked_projects = scoring_service.rank_experiences_and_projects(
            resume, job_analysis
        )
        
        logger.info(f"Job analysis completed for {job_id}")
        return JobAnalysisResult(
            job_analysis=job_analysis,
            ranked_experiences=ranked_experiences,
            ranked_projects=ranked_projects
        )
        
    except ValueError as e:
        logger.warning(f"Job not found: {job_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Job analysis failed for {job_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Job analysis failed"
        )

@app.get("/api/resume/versions")
async def get_resume_versions(resume_service: ResumeService = Depends(get_resume_service)):
    """
    List all job-specific resume versions.
    
    Returns:
        Dictionary containing list of available resume version identifiers
        
    Raises:
        HTTPException: If listing operation fails
    """
    try:
        versions = resume_service.list_resume_versions()
        logger.info(f"Listed {len(versions)} resume versions")
        return {"versions": versions}
    except Exception as e:
        logger.error(f"Failed to list resume versions: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to list resume versions"
        )


@app.get("/api/resume/versions/{job_id}")
async def get_resume_version(
    job_id: str, 
    resume_service: ResumeService = Depends(get_resume_service)
):
    """
    Get job-specific resume version.
    
    Args:
        job_id: Job identifier for specific resume version
        
    Returns:
        Job-optimized resume data
        
    Raises:
        HTTPException: If version not found (404) or loading fails (500)
    """
    try:
        version = resume_service.load_resume_version(job_id)
        if version:
            logger.info(f"Retrieved resume version for job {job_id}")
            return version
        else:
            logger.warning(f"No resume version found for job {job_id}")
            raise HTTPException(
                status_code=404, 
                detail=f"No resume version found for job {job_id}"
            )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Failed to load resume version for {job_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to load resume version"
        )

@app.get("/api/resume/sample")
async def get_sample_resume():
    """
    Get sample resume data for testing and development.
    
    Loads predefined sample resume with realistic data for testing
    the resume optimization system.
    
    Returns:
        Resume object with sample data
        
    Raises:
        HTTPException: If sample data cannot be loaded
    """
    try:
        sample_path = Path(__file__).parent.parent / "data" / "sample_data" / "sample_resume.json"
        
        if not sample_path.exists():
            logger.error(f"Sample resume file not found: {sample_path}")
            raise HTTPException(
                status_code=500, 
                detail="Sample resume data not available"
            )
        
        with open(sample_path, 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
        
        logger.info("Sample resume data loaded successfully")
        return Resume(**sample_data)
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in sample resume file: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Sample resume data is corrupted"
        )
    except Exception as e:
        logger.error(f"Failed to load sample resume: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to load sample resume data"
        )
