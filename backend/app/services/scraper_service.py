"""
Scraper service: loads/saves settings and executes jobspy scrapes.

The original CLI script (backend/scripts/scrap_job.py) is left intact for
manual use. This service extracts the same logic and adapts it to use
SQLAlchemy so it integrates cleanly with the rest of the FastAPI app.
"""

import json
import logging
import os
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.scraper import ScraperSettings

logger = logging.getLogger(__name__)

# Path to the persisted settings file
SETTINGS_PATH = Path(__file__).parent.parent.parent / "data" / "scraper_settings.json"

# Columns returned by jobspy that we don't store in the DB
UNWANTED_COLUMNS = [
    "salary_source",
    "interval",
    "min_amount",
    "max_amount",
    "currency",
    "job_function",
    "job_level",
    "listing_type",
    "vacancy_count",
    "company_industry",
    "company_logo",
    "company_addresses",
    "company_num_employees",
    "company_revenue",
    "company_description",
    "company_rating",
    "company_reviews_count",
    "emails",
    "work_from_home_type",
]

# Columns we actually insert (must match the job_list table schema)
INSERT_COLUMNS = [
    "id",
    "site",
    "job_url",
    "job_url_direct",
    "title",
    "company",
    "location",
    "date_posted",
    "job_type",
    "is_remote",
    "description",
    "company_url",
    "company_url_direct",
    "skills",
    "experience_range",
]


class ScraperService:
    """Manages scraper settings persistence and executes jobspy scrapes."""

    # ------------------------------------------------------------------ #
    #  Settings I/O                                                        #
    # ------------------------------------------------------------------ #

    def load_settings(self) -> ScraperSettings:
        """Load settings from JSON file, returning defaults if missing or corrupt."""
        try:
            if SETTINGS_PATH.exists():
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return ScraperSettings(**data)
        except Exception as e:
            logger.warning(f"Could not load scraper settings, using defaults: {e}")
        return ScraperSettings()

    def save_settings(self, settings: ScraperSettings) -> None:
        """
        Persist settings atomically.

        Writes to a temp file in the same directory then renames, so a crash
        mid-write never leaves a corrupt settings file.
        """
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = settings.model_dump()

        fd, tmp_path = tempfile.mkstemp(
            dir=SETTINGS_PATH.parent, suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, SETTINGS_PATH)
            logger.info("Scraper settings saved.")
        except Exception:
            # Clean up temp file if rename failed
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    # ------------------------------------------------------------------ #
    #  Scrape execution                                                    #
    # ------------------------------------------------------------------ #

    def run_scrape(self, db: Session) -> Dict[str, Any]:
        """
        Execute a jobspy scrape using current settings.

        Inserts new jobs into SQLite via INSERT OR IGNORE (deduplication by
        primary key). Returns a summary dict with jobs_found, jobs_added,
        and ran_at (ISO timestamp).

        Args:
            db: SQLAlchemy session (injected by the caller).

        Returns:
            {
                "jobs_found": int,
                "jobs_added": int,
                "ran_at": str   # ISO 8601 UTC
            }
        """
        # Import here so a missing jobspy install only fails at scrape time,
        # not at application startup.
        try:
            from jobspy import scrape_jobs
        except ImportError as e:
            raise RuntimeError(
                "jobspy is not installed. Add 'jobspy' to requirement.txt and reinstall."
            ) from e

        settings = self.load_settings()
        ran_at = datetime.now(timezone.utc).isoformat()

        # Auto-expire jobs older than 60 days before inserting new ones
        cutoff = (datetime.now(timezone.utc) - timedelta(days=60)).strftime("%Y-%m-%d")
        expired = db.execute(text("DELETE FROM job_list WHERE date_posted < :cutoff"), {"cutoff": cutoff})
        db.commit()
        if expired.rowcount:
            logger.info(f"Auto-expired {expired.rowcount} jobs older than {cutoff}.")

        logger.info(
            f"Starting scrape — term='{settings.search_term}' "
            f"location='{settings.location}' country='{settings.country}' "
            f"sites={settings.sites} results_wanted={settings.results_wanted}"
        )

        jobs_df = scrape_jobs(
            site_name=settings.sites,
            search_term=settings.search_term,
            location=settings.location,
            results_wanted=settings.results_wanted,
            hours_old=settings.hours_old,
            country_indeed=settings.country,
        )

        jobs_found = len(jobs_df)
        logger.info(f"jobspy returned {jobs_found} jobs")

        # Drop unwanted columns (ignore if not present)
        jobs_df = jobs_df.drop(columns=UNWANTED_COLUMNS, errors="ignore")

        # Ensure all expected columns exist (fill missing with None)
        for col in INSERT_COLUMNS:
            if col not in jobs_df.columns:
                jobs_df[col] = None

        insert_sql = text("""
            INSERT OR IGNORE INTO job_list
                (id, site, job_url, job_url_direct, title, company,
                 location, date_posted, job_type, is_remote, description,
                 company_url, company_url_direct, skills, experience_range)
            VALUES
                (:id, :site, :job_url, :job_url_direct, :title, :company,
                 :location, :date_posted, :job_type, :is_remote, :description,
                 :company_url, :company_url_direct, :skills, :experience_range)
        """)

        jobs_added = 0
        for _, row in jobs_df[INSERT_COLUMNS].iterrows():
            row_dict = {col: (None if _is_na(row[col]) else row[col]) for col in INSERT_COLUMNS}
            result = db.execute(insert_sql, row_dict)
            jobs_added += result.rowcount

        db.commit()
        logger.info(f"Scrape complete: {jobs_added} new jobs added out of {jobs_found} found.")

        return {
            "jobs_found": jobs_found,
            "jobs_added": jobs_added,
            "ran_at": ran_at,
        }


# ------------------------------------------------------------------ #
#  Helpers                                                             #
# ------------------------------------------------------------------ #

def _is_na(value: Any) -> bool:
    """Return True if value is pandas NA / NaN / None."""
    if value is None:
        return True
    try:
        import math
        if isinstance(value, float) and math.isnan(value):
            return True
    except (TypeError, ValueError):
        pass
    # pandas NA
    try:
        import pandas as pd
        if pd.isna(value):
            return True
    except (TypeError, ValueError, ImportError):
        pass
    return False
