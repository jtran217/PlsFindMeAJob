"""
Pydantic models for the job scraper settings and status.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

VALID_SITES = ["indeed", "linkedin", "glassdoor", "zip_recruiter"]


class ScraperSettings(BaseModel):
    search_term: str = "computer science"
    location: str = "Calgary"
    country: str = "canada"
    interval_hours: int = Field(default=24, ge=1, le=168)  # 1 hour to 1 week
    results_wanted: int = Field(default=20, ge=1, le=100)
    hours_old: int = Field(default=72, ge=1, le=720)
    sites: List[Literal["indeed", "linkedin", "glassdoor", "zip_recruiter"]] = Field(
        default_factory=lambda: list(VALID_SITES)
    )
    enabled: bool = True


class ScraperStatus(BaseModel):
    last_run: Optional[str] = None       # ISO timestamp or None
    last_run_jobs_found: int = 0
    last_run_jobs_added: int = 0
    is_running: bool = False
    next_run: Optional[str] = None       # ISO timestamp of next scheduled run
    enabled: bool = True
