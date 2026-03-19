"""
PlsFindMeAJob FastAPI Application.

Main application entry point providing REST API endpoints for:
- Job management (existing functionality)
- Resume optimization and scoring system
- Job-specific resume analysis and ranking
- PDF generation and download
"""

import json
import logging
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Generator, List, Optional

from dotenv import load_dotenv

# Load environment variables from project root .env before any service imports
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent.parent / ".env")

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import SessionLocal, engine, Base
from app.job_models import Job
from app.models.resume import Resume, JobAnalysisResult, OptimizedContent, OptimizedResume
from app.models.scraper import ScraperSettings, ScraperStatus
from app.services.resume_service import ResumeService
from app.services.scoring_service import ScoringService
from app.services.optimization_service import OptimizationService
from app.services.pdf_service import PDFService
from app.services.scraper_service import ScraperService

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

# ---------------------------------------------------------------------------
# Application startup: initialize singleton services and the APScheduler.
# Two startup handlers are registered — FastAPI calls both in order.
# ---------------------------------------------------------------------------

@app.on_event("startup")
def _startup() -> None:
    """Initialise singleton services and attach them to app.state."""
    try:
        app.state.optimization_service = OptimizationService()
        logger.info("OptimizationService initialised successfully.")
    except EnvironmentError as e:
        logger.error(f"OptimizationService could not be initialised: {e}")
        app.state.optimization_service = None

    # Initialise the scraper service and its in-memory status store
    app.state.scraper_service = ScraperService()
    app.state.scraper_status = {
        "last_run": None,
        "last_run_jobs_found": 0,
        "last_run_jobs_added": 0,
        "is_running": False,
        "next_run": None,
    }
    logger.info("ScraperService initialised.")


@app.on_event("startup")
async def _start_scheduler() -> None:
    """Start APScheduler and register the periodic scrape job if enabled."""
    scraper_svc: ScraperService = app.state.scraper_service
    settings = scraper_svc.load_settings()

    scheduler = AsyncIOScheduler()

    if settings.enabled:
        scheduler.add_job(
            _scheduled_scrape,
            trigger="interval",
            hours=settings.interval_hours,
            id="job_scraper",
            replace_existing=True,
        )
        logger.info(
            f"Scraper scheduled every {settings.interval_hours}h (enabled={settings.enabled})."
        )
        # Compute next run time after the scheduler starts (below)

    scheduler.start()
    app.state.scheduler = scheduler

    # Update next_run in status after scheduler has started
    if settings.enabled:
        _refresh_next_run()


async def _scheduled_scrape() -> None:
    """Wrapper called by APScheduler; opens its own DB session."""
    db = SessionLocal()
    try:
        await _do_scrape(db)
    finally:
        db.close()


async def _do_scrape(db: Session) -> None:
    """
    Core scrape logic shared by the scheduler and the /run endpoint.
    Guards against concurrent runs via the is_running flag.

    The jobspy call is blocking (network I/O + pandas), so it is offloaded
    to a thread-pool executor to avoid stalling the event loop.
    """
    import asyncio
    status: Dict[str, Any] = app.state.scraper_status

    if status["is_running"]:
        logger.warning("Scrape requested but one is already running — skipping.")
        return

    status["is_running"] = True
    try:
        scraper_svc: ScraperService = app.state.scraper_service
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, scraper_svc.run_scrape, db)
        status["last_run"] = result["ran_at"]
        status["last_run_jobs_found"] = result["jobs_found"]
        status["last_run_jobs_added"] = result["jobs_added"]
        logger.info(
            f"Scrape finished: {result['jobs_added']} added / {result['jobs_found']} found."
        )
    except Exception as e:
        logger.error(f"Scrape failed: {e}")
    finally:
        status["is_running"] = False
        _refresh_next_run()


def _refresh_next_run() -> None:
    """Update app.state.scraper_status['next_run'] from the scheduler."""
    try:
        scheduler: AsyncIOScheduler = app.state.scheduler
        job = scheduler.get_job("job_scraper")
        if job and job.next_run_time:
            app.state.scraper_status["next_run"] = job.next_run_time.isoformat()
        else:
            app.state.scraper_status["next_run"] = None
    except Exception:
        app.state.scraper_status["next_run"] = None

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

# ---------------------------------------------------------------------------
# Dependency injection
# ---------------------------------------------------------------------------

def get_db() -> Generator[Session, None, None]:
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_resume_service() -> ResumeService:
    """Resume service dependency injection."""
    return ResumeService()


def get_scoring_service(db: Session = Depends(get_db)) -> ScoringService:
    """Scoring service dependency injection."""
    return ScoringService(db)


def get_optimization_service() -> OptimizationService:
    """
    Return the singleton OptimizationService from app.state.

    The service is initialised once at startup so the underlying
    AsyncOpenAI (httpx) client is reused across requests rather than
    being created and discarded on every call.

    Raises:
        HTTPException: If OPENROUTER_API_KEY was not configured at startup.
    """
    svc = getattr(app.state, "optimization_service", None)
    if svc is None:
        raise HTTPException(
            status_code=500,
            detail="AI optimization service is not configured. OPENROUTER_API_KEY is missing."
        )
    return svc


def get_pdf_service() -> PDFService:
    """PDF generation service dependency injection."""
    return PDFService()


def get_scraper_service() -> ScraperService:
    """Return the singleton ScraperService from app.state."""
    return app.state.scraper_service


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def root() -> Dict[str, str]:
    """Root endpoint — API health check."""
    return {"message": "PlsFindMeAJob API is running"}


@app.get("/api/jobs")
def get_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get paginated jobs sorted by date_posted descending.

    Returns:
        Paginated response with items, total, page, page_size, total_pages.

    Raises:
        HTTPException: If database query fails.
    """
    try:
        query = db.query(Job).order_by(Job.date_posted.desc())
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        total_pages = max(1, math.ceil(total / page_size))
        logger.info(f"Retrieved {len(items)} jobs (page {page}/{total_pages}, total={total})")
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve jobs from database")
    except Exception as e:
        logger.error(f"Unexpected error retrieving jobs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


class JobStatusUpdate(BaseModel):
    status: str


@app.patch("/api/jobs/{job_id}/status")
def update_job_status(job_id: str, body: JobStatusUpdate, db: Session = Depends(get_db)):
    """Update the status of a single job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    job.status = body.status
    db.commit()
    db.refresh(job)
    logger.info(f"Updated job {job_id} status to {body.status}")
    return job


@app.delete("/api/jobs/{job_id}", status_code=204)
def delete_job(job_id: str, db: Session = Depends(get_db)):
    """Hard-delete a single job by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    db.delete(job)
    db.commit()
    logger.info(f"Deleted job {job_id}")


@app.post("/api/jobs/cleanup")
def cleanup_old_jobs(db: Session = Depends(get_db)):
    """Delete all jobs with date_posted older than 60 days."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=60)).strftime("%Y-%m-%d")
    deleted = db.query(Job).filter(Job.date_posted < cutoff).delete()
    db.commit()
    logger.info(f"Cleanup deleted {deleted} jobs older than {cutoff}")
    return {"deleted": deleted}


# ---------------------------------------------------------------------------
# Resume Management Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/resume", response_model=Resume)
async def get_resume(resume_service: ResumeService = Depends(get_resume_service)):
    """
    Get master resume data. Returns empty structure if none exists.
    """
    try:
        resume = resume_service.load_master_resume()
        logger.info("Master resume retrieved successfully")
        return resume
    except Exception as e:
        logger.error(f"Failed to load master resume: {e}")
        raise HTTPException(status_code=500, detail="Failed to load resume data")


@app.post("/api/resume")
async def save_resume(
    resume_data: Resume,
    resume_service: ResumeService = Depends(get_resume_service)
):
    """Save or update master resume data."""
    try:
        success = resume_service.save_master_resume(resume_data)
        if success:
            logger.info("Master resume saved successfully")
            return {"success": True, "message": "Resume saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save resume")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving resume: {e}")
        raise HTTPException(status_code=500, detail="Failed to save resume data")


@app.put("/api/resume")
async def update_resume(
    resume_data: Resume,
    resume_service: ResumeService = Depends(get_resume_service)
):
    """Update master resume data (equivalent to POST, signals replace intent)."""
    try:
        success = resume_service.save_master_resume(resume_data)
        if success:
            logger.info("Master resume updated successfully")
            return {"success": True, "message": "Resume updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update resume")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating resume: {e}")
        raise HTTPException(status_code=500, detail="Failed to update resume data")


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

    Loads the master resume and the target job, filters to selected
    experiences and projects, then sends each item's bullets to OpenRouter
    in a single concurrent batch. Results are saved as a resume version.

    Cost: ~$0.010 per run with claude-3.5-haiku (per-item batching).
    On failure for any item, falls back to original bullet text.
    """
    try:
        logger.info(
            f"Optimization requested for job {job_id} — "
            f"{len(request.selected_experiences)} experiences, "
            f"{len(request.selected_projects)} projects"
        )

        resume = resume_service.load_master_resume()

        # extract_job_requirements raises ValueError if the job doesn't exist.
        # Catch it here before we ever reach the AI service, so a missing-job
        # error returns 404 and an AI-level ValueError returns 500.
        try:
            job_analysis = scoring_service.extract_job_requirements(job_id)
        except ValueError as e:
            logger.warning(f"Job not found during optimization: {job_id}")
            raise HTTPException(status_code=404, detail=str(e))

        job_description = job_analysis.job_description

        exp_id_set = set(request.selected_experiences)
        proj_id_set = set(request.selected_projects)

        selected_experiences = [e for e in resume.experiences if e.id in exp_id_set]
        selected_projects = [p for p in resume.projects if p.id in proj_id_set]

        if not selected_experiences and not selected_projects:
            raise HTTPException(
                status_code=400,
                detail="None of the provided IDs were found in the master resume."
            )

        optimized_content = await optimization_service.optimize_resume_items(
            selected_experiences=selected_experiences,
            selected_projects=selected_projects,
            job_description=job_description,
            job_title=job_analysis.job_title,
            company=job_analysis.company,
        )

        resume_version = OptimizedResume(
            job_id=job_id,
            generated_at="",
            selected_experiences=request.selected_experiences,
            selected_projects=request.selected_projects,
            optimized_content=optimized_content,
        )
        resume_service.save_resume_version(job_id, resume_version)

        logger.info(f"Optimization complete and saved for job {job_id}")
        return optimized_content

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Optimization failed for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Resume optimization failed. Please try again.")


@app.post("/api/resume/generate-pdf/{job_id}")
async def generate_resume_pdf(
    job_id: str,
    finalized_content: OptimizedContent,
    resume_service: ResumeService = Depends(get_resume_service),
    pdf_service: PDFService = Depends(get_pdf_service),
):
    """
    Generate a LaTeX PDF resume for a specific job.

    Combines the master resume with finalized (reviewed + edited) optimized
    content and compiles a professional PDF using the Jake Resume template.

    Args:
        job_id:            Target job identifier.
        finalized_content: Reviewed and approved optimized bullet points.

    Returns:
        JSON with the generated PDF filename and download URL.

    Raises:
        HTTPException: 404 if resume version not found, 500 if compilation fails.
    """
    try:
        logger.info(f"PDF generation requested for job {job_id}")

        # Load master resume for personal info, education, skills
        resume = resume_service.load_master_resume()

        # Load resume version for selected IDs
        version = resume_service.load_resume_version(job_id)
        if not version:
            raise HTTPException(
                status_code=404,
                detail=f"No optimized resume version found for job {job_id}. "
                       f"Run /api/resume/optimize/{job_id} first."
            )

        pdf_path = pdf_service.generate_resume_pdf(
            job_id=job_id,
            personal_info=resume.personal_info,
            education=resume.education,
            technical_skills=resume.technical_skills,
            selected_experience_ids=version.selected_experiences,
            selected_project_ids=version.selected_projects,
            all_experiences=resume.experiences,
            all_projects=resume.projects,
            optimized_content=finalized_content,
        )

        logger.info(f"PDF generated for job {job_id}: {pdf_path.name}")
        return {
            "success": True,
            "filename": pdf_path.name,
            "download_url": f"/api/resume/download/{job_id}",
        }

    except HTTPException:
        raise
    except FileNotFoundError as e:
        logger.error(f"Template missing for PDF generation: {e}")
        raise HTTPException(
            status_code=500,
            detail="LaTeX template not found. Ensure backend/templates/jake_resume.tex exists."
        )
    except RuntimeError as e:
        logger.error(f"PDF compilation failed for job {job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"PDF compilation failed. Ensure pdflatex is installed. Details: {str(e)[:500]}"
        )
    except Exception as e:
        logger.error(f"Unexpected PDF generation error for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="PDF generation failed unexpectedly.")


@app.get("/api/resume/download/{job_id}")
async def download_resume_pdf(
    job_id: str,
    pdf_service: PDFService = Depends(get_pdf_service),
):
    """
    Download the most recently generated PDF for a specific job.

    Args:
        job_id: Job identifier.

    Returns:
        PDF file as a binary response with Content-Disposition: attachment.

    Raises:
        HTTPException: 404 if no PDF has been generated for this job yet.
    """
    pdf_path = pdf_service.find_latest_pdf(job_id)
    if not pdf_path or not pdf_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No PDF found for job {job_id}. Generate one first via POST /api/resume/generate-pdf/{job_id}."
        )

    logger.info(f"Serving PDF download for job {job_id}: {pdf_path.name}")
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"resume_{job_id}.pdf",
    )


@app.post("/api/resume/analyze/{job_id}", response_model=JobAnalysisResult)
async def analyze_job_for_resume(
    job_id: str,
    resume_service: ResumeService = Depends(get_resume_service),
    scoring_service: ScoringService = Depends(get_scoring_service)
):
    """
    Analyze job requirements and rank resume items by relevance.

    Extracts keywords and technologies from the job posting, then scores
    and ranks all resume experiences and projects.
    """
    try:
        logger.info(f"Starting job analysis for job_id: {job_id}")

        resume = resume_service.load_master_resume()
        job_analysis = scoring_service.extract_job_requirements(job_id)
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
        raise HTTPException(status_code=500, detail="Job analysis failed")


@app.get("/api/resume/versions")
async def get_resume_versions(resume_service: ResumeService = Depends(get_resume_service)):
    """List all job-specific resume versions."""
    try:
        versions = resume_service.list_resume_versions()
        logger.info(f"Listed {len(versions)} resume versions")
        return {"versions": versions}
    except Exception as e:
        logger.error(f"Failed to list resume versions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list resume versions")


@app.get("/api/resume/versions/{job_id}")
async def get_resume_version(
    job_id: str,
    resume_service: ResumeService = Depends(get_resume_service)
):
    """Get job-specific resume version."""
    try:
        version = resume_service.load_resume_version(job_id)
        if version:
            logger.info(f"Retrieved resume version for job {job_id}")
            return version
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No resume version found for job {job_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load resume version for {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load resume version")


@app.get("/api/resume/sample")
async def get_sample_resume():
    """
    Get sample resume data for testing and development.

    Returns:
        Resume object with pre-populated sample data.
    """
    try:
        sample_path = Path(__file__).parent.parent / "data" / "sample_data" / "sample_resume.json"

        if not sample_path.exists():
            logger.error(f"Sample resume file not found: {sample_path}")
            raise HTTPException(status_code=500, detail="Sample resume data not available")

        with open(sample_path, 'r', encoding='utf-8') as f:
            sample_data = json.load(f)

        logger.info("Sample resume data loaded successfully")
        return Resume(**sample_data)

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in sample resume file: {e}")
        raise HTTPException(status_code=500, detail="Sample resume data is corrupted")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load sample resume: {e}")
        raise HTTPException(status_code=500, detail="Failed to load sample resume data")


# ---------------------------------------------------------------------------
# Scraper API Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/scraper/settings", response_model=ScraperSettings)
async def get_scraper_settings(
    scraper_service: ScraperService = Depends(get_scraper_service),
):
    """Return current scraper settings."""
    return scraper_service.load_settings()


@app.put("/api/scraper/settings", response_model=ScraperSettings)
async def update_scraper_settings(
    settings: ScraperSettings,
    scraper_service: ScraperService = Depends(get_scraper_service),
):
    """
    Save new scraper settings and reschedule (or remove) the APScheduler job
    to reflect the new interval_hours and enabled flag.
    """
    try:
        scraper_service.save_settings(settings)

        scheduler = getattr(app.state, "scheduler", None)
        if scheduler is not None:
            existing_job = scheduler.get_job("job_scraper")

            if settings.enabled:
                if existing_job:
                    scheduler.reschedule_job(
                        "job_scraper",
                        trigger="interval",
                        hours=settings.interval_hours,
                    )
                    logger.info(
                        f"Scraper rescheduled to every {settings.interval_hours}h."
                    )
                else:
                    scheduler.add_job(
                        _scheduled_scrape,
                        trigger="interval",
                        hours=settings.interval_hours,
                        id="job_scraper",
                        replace_existing=True,
                    )
                    logger.info(
                        f"Scraper job added at every {settings.interval_hours}h."
                    )
                _refresh_next_run()
            else:
                if existing_job:
                    scheduler.remove_job("job_scraper")
                    logger.info("Scraper job removed (disabled).")
                app.state.scraper_status["next_run"] = None

        return settings

    except Exception as e:
        logger.error(f"Failed to update scraper settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to save scraper settings.")


@app.post("/api/scraper/run")
async def run_scraper_now(db: Session = Depends(get_db)):
    """
    Trigger an immediate scrape outside the normal schedule.

    Returns 409 if a scrape is already in progress.
    """
    status = app.state.scraper_status
    if status["is_running"]:
        raise HTTPException(
            status_code=409,
            detail="A scrape is already in progress. Please wait for it to finish.",
        )

    import asyncio
    asyncio.create_task(_do_scrape(db))

    return {"message": "Scrape started."}


@app.get("/api/scraper/status", response_model=ScraperStatus)
async def get_scraper_status(
    scraper_service: ScraperService = Depends(get_scraper_service),
):
    """
    Return last run time, jobs found/added, whether a run is currently in
    progress, the next scheduled run time, and the enabled flag.
    """
    raw = app.state.scraper_status
    settings = scraper_service.load_settings()
    return ScraperStatus(
        last_run=raw["last_run"],
        last_run_jobs_found=raw["last_run_jobs_found"],
        last_run_jobs_added=raw["last_run_jobs_added"],
        is_running=raw["is_running"],
        next_run=raw["next_run"],
        enabled=settings.enabled,
    )
