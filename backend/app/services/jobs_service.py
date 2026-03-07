"""
Jobs service for handling job-related business logic.

This module contains the JobsService class which encapsulates all job-related
operations including querying, filtering, and pagination.
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.models.database import Job
from app.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class JobsService:
    """Service class for handling job-related operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the jobs service.
        
        Args:
            db: Database session for performing operations
        """
        self.db = db
    
    def get_jobs_paginated(self, skip: int = 0, limit: int = 15, status: Optional[str] = None) -> Dict[str, Any]:
        """
        Get paginated job listings with total count.
        
        Args:
            skip: Number of jobs to skip for pagination
            limit: Maximum number of jobs to return
            status: Optional status filter ('ready', 'applied', 'all', etc.)
            
        Returns:
            Dictionary containing total count and job data
            
        Raises:
            ValidationError: If pagination parameters are invalid
        """
        # Validate pagination parameters
        if skip < 0:
            raise ValidationError("Skip parameter cannot be negative")
        if limit <= 0:
            raise ValidationError("Limit parameter must be positive")
        if limit > 100:  # Reasonable upper limit
            raise ValidationError("Limit parameter cannot exceed 100")
        
        try:
            # Build base query
            query = self.db.query(Job)
            
            # Apply status filter if provided
            if status:
                query = query.filter(Job.status == status)
            
            # Get total count of jobs (after filtering)
            total = query.count()
            logger.info(f"Total jobs in database{f' with status {status}' if status else ''}: {total}")
            
            # Get paginated jobs
            jobs = query.offset(skip).limit(limit).all()
            logger.info(f"Retrieved {len(jobs)} jobs (skip={skip}, limit={limit}, status={status})")
            
            return {
                "total": total,
                "data": jobs
            }
            
        except Exception as e:
            logger.error(f"Error retrieving jobs: {str(e)}")
            raise ValidationError(f"Failed to retrieve jobs: {str(e)}")
    
    def get_job_by_id(self, job_id: str) -> Job:
        """
        Get a specific job by ID.
        
        Args:
            job_id: The ID of the job to retrieve
            
        Returns:
            Job object if found
            
        Raises:
            ValidationError: If job is not found
        """
        if not job_id or job_id.strip() == "":
            raise ValidationError("Job ID cannot be empty")
            
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValidationError(f"Job with ID {job_id} not found")
            
        return job
    
    def get_jobs_count_by_status(self) -> Dict[str, int]:
        """
        Get the count of jobs grouped by status.
        
        Returns:
            Dictionary mapping status to count
        """
        try:
            from sqlalchemy import func
            result = self.db.query(Job.status, func.count(Job.id)).group_by(Job.status).all()
            
            counts = {}
            total = 0
            for status, count in result:
                counts[status] = count
                total += count
            
            # Add total count
            counts['total'] = total
            
            logger.info(f"Job counts by status: {counts}")
            return counts
        except Exception as e:
            logger.error(f"Error counting jobs by status: {str(e)}")
            raise ValidationError(f"Failed to count jobs by status: {str(e)}")
    
    def get_jobs_count(self) -> int:
        """
        Get the total number of jobs in the database.
        
        Returns:
            Total count of jobs
        """
        try:
            count = self.db.query(Job).count()
            logger.info(f"Total jobs count: {count}")
            return count
        except Exception as e:
            logger.error(f"Error counting jobs: {str(e)}")
            raise ValidationError(f"Failed to count jobs: {str(e)}")
    
    def search_jobs(self, search_term: str, skip: int = 0, limit: int = 15) -> Dict[str, Any]:
        """
        Search jobs by title or company name.
        
        Args:
            search_term: Term to search for in job title or company
            skip: Number of jobs to skip for pagination
            limit: Maximum number of jobs to return
            
        Returns:
            Dictionary containing total count and matching job data
        """
        # Validate inputs
        if not search_term or search_term.strip() == "":
            raise ValidationError("Search term cannot be empty")
        if skip < 0:
            raise ValidationError("Skip parameter cannot be negative")
        if limit <= 0:
            raise ValidationError("Limit parameter must be positive")
        if limit > 100:
            raise ValidationError("Limit parameter cannot exceed 100")
        
        try:
            search_term = search_term.strip().lower()
            
            # Build query with case-insensitive search
            query = self.db.query(Job).filter(
                (Job.title.ilike(f"%{search_term}%")) |
                (Job.company.ilike(f"%{search_term}%"))
            )
            
            # Get total count of matching jobs
            total = query.count()
            
            # Get paginated results
            jobs = query.offset(skip).limit(limit).all()
            
            logger.info(f"Search for '{search_term}' found {total} jobs, returning {len(jobs)}")
            
            return {
                "total": total,
                "data": jobs,
                "search_term": search_term
            }
            
        except Exception as e:
            logger.error(f"Error searching jobs: {str(e)}")
            raise ValidationError(f"Failed to search jobs: {str(e)}")