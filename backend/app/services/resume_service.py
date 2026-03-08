"""
Resume service for the enhanced resume system.
Handles all operations for the new resume optimization format.
"""
import logging
from typing import Dict, Any, Optional, List
from pydantic import ValidationError
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    ProfileException,
    ProfileValidationError,
    ProfileCorruptedError,
    FileOperationError,
    ProfilePermissionError,
    RxResumeAPIError,
    RxResumeAuthenticationError,
    RxResumeValidationError,
    RxResumeNotFoundError,
    RxResumeNetworkError,
    RxResumeSlugExistsError
)
from app.models.resume_schemas import Resume, ResumeResponse, ResumeSaveResponse, ResumeData, EnhancedBasics
from app.models.rxresume_schemas import (
    ResumeJobCreate,
    ResumeJobResponse,
    ResumeJobListResponse,
    BulkSyncRequest,
    BulkSyncResponse
)
from app.models.database import ResumeJob, Job
from app.database import SessionLocal
from app.utils.rxresume_client import RxResumeClient
from app.utils.resume_transformers import ResumeTransformer

logger = logging.getLogger(__name__)


class ResumeService:
    """Service class for handling all resume-related business logic."""
    
    def __init__(self):
        """Initialize ResumeService."""
        self.resume_path = Path(settings.PROFILE_PATH).parent / "resume.json"
        self.rxresume_client = RxResumeClient()
        self.transformer = ResumeTransformer()
    
    async def get_resume(self) -> Resume:
        """
        Retrieve user resume with proper validation.
        
        Returns:
            Resume: Validated resume data or default resume if not found
            
        Raises:
            ProfileException: For resume-related errors
            FileOperationError: For file I/O errors
        """
        try:
            if self.resume_path.exists():
                try:
                    resume_data = self._load_resume_data()
                    validated_resume = Resume(**resume_data)
                    logger.debug("Resume loaded successfully from resume.json")
                    return validated_resume
                except (ValidationError, ProfileCorruptedError) as e:
                    logger.warning(f"Resume file corrupted, returning default: {e}")
                    return self._get_default_resume()
            else:
                logger.info("No resume file found, returning default")
                return self._get_default_resume()
                
        except FileOperationError as e:
            logger.error(f"File operation failed: {e}")
            raise ProfileException(f"Failed to load resume: {e}")
            
        except Exception as e:
            logger.error(f"Unexpected error loading resume: {e}")
            raise ProfileException(f"Unexpected error loading resume: {e}")
    
    async def save_resume(self, resume_data: Dict[str, Any], job_id: str = None) -> ResumeSaveResponse:
        """
        Save user resume with validation and error handling.
        Enhanced with automatic RxResume sync for job-specific resumes.
        
        Args:
            resume_data: Raw resume data dictionary
            job_id: Optional job ID to trigger automatic sync
            
        Returns:
            ResumeSaveResponse: Result of save operation
            
        Raises:
            ProfileValidationError: For validation errors
            ProfilePermissionError: For permission errors
            ProfileException: For other resume-related errors
        """
        try:
            try:
                validated_resume = Resume(**resume_data)
                logger.debug("Resume data validated successfully")
                
            except ValidationError as e:
                errors = {}
                for error in e.errors():
                    field = '.'.join(str(loc) for loc in error['loc'])
                    errors[field] = error['msg']
                
                logger.warning(f"Resume validation failed: {errors}")
                raise ProfileValidationError(
                    "Resume validation failed", 
                    validation_errors=errors
                )
            
            self._save_resume_data(validated_resume.dict())
            
            logger.info("Resume saved successfully")
            
            # Automatic sync to RxResume if job_id provided
            if job_id is not None:
                try:
                    await self._auto_sync_to_rxresume(job_id)
                    logger.debug(f"Auto-sync to RxResume completed for job {job_id}")
                except Exception as e:
                    logger.error(f"Auto-sync to RxResume failed for job {job_id}: {e}")
                    # Don't fail the save operation, just log the sync failure
            
            return ResumeSaveResponse(
                success=True,
                message="Resume saved successfully!"
            )
            
        except ProfileValidationError:
            # Re-raise validation errors
            raise
            
        except ProfilePermissionError as e:
            logger.error(f"Permission error saving resume: {e}")
            raise ProfileException(f"Permission denied: Cannot save resume - {e}")
            
        except FileOperationError as e:
            logger.error(f"File operation failed: {e}")
            raise ProfileException(f"Failed to save resume: {e}")
            
        except Exception as e:
            logger.error(f"Unexpected error saving resume: {e}")
            raise ProfileException(f"Unexpected error saving resume: {e}")
    
    async def validate_resume_data(self, resume_data: Dict[str, Any]) -> Resume:
        """
        Validate resume data without saving.
        
        Args:
            resume_data: Raw resume data dictionary
            
        Returns:
            Resume: Validated resume instance
            
        Raises:
            ProfileValidationError: If validation fails
        """
        try:
            validated_resume = Resume(**resume_data)
            logger.debug("Resume data validation successful")
            return validated_resume
            
        except ValidationError as e:
            errors = {}
            for error in e.errors():
                field = '.'.join(str(loc) for loc in error['loc'])
                errors[field] = error['msg']
            
            logger.warning(f"Resume validation failed: {errors}")
            raise ProfileValidationError(
                "Resume validation failed",
                validation_errors=errors
            )
    
    def _load_resume_data(self) -> Dict[str, Any]:
        """Load resume data from file."""
        try:
            with open(self.resume_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"Resume data loaded from {self.resume_path}")
            return data
        except FileNotFoundError:
            raise FileOperationError(f"Resume file not found: {self.resume_path}")
        except json.JSONDecodeError as e:
            raise ProfileCorruptedError(f"Invalid JSON in resume file: {e}")
        except PermissionError:
            raise ProfilePermissionError(f"Permission denied accessing: {self.resume_path}")
        except Exception as e:
            raise FileOperationError(f"Error reading resume file: {e}")
    
    def _save_resume_data(self, resume_data: Dict[str, Any]) -> None:
        """Save resume data to file."""
        try:
            self.resume_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.resume_path, 'w', encoding='utf-8') as f:
                json.dump(resume_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Resume data saved to {self.resume_path}")
            
        except PermissionError:
            raise ProfilePermissionError(f"Permission denied writing to: {self.resume_path}")
        except Exception as e:
            raise FileOperationError(f"Error writing resume file: {e}")
    
    def _get_default_resume(self) -> Resume:
        """
        Create a default resume with minimal data.
        
        Returns:
            Resume: Default resume instance
        """
        basics = EnhancedBasics(
            name="",
            email="",
            phone="",
            headline="",
            location=""
        )
        
        resume_data = ResumeData(basics=basics)
        
        return Resume(
            name="My Resume",
            slug="my-resume",
            tags=["Technology"],
            data=resume_data,
            isPublic=True
        )
    
    def get_resume_path(self) -> Path:
        """Get the resume file path."""
        return self.resume_path
    
    def backup_resume(self, backup_path: Optional[str] = None) -> str:
        """
        Create a backup of the current resume.
        
        Args:
            backup_path: Custom backup path, or auto-generate if None
            
        Returns:
            str: Path to backup file
        """
        try:
            if not self.resume_path.exists():
                raise FileOperationError("No resume file to backup")
            
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = str(self.resume_path.parent / f"resume_backup_{timestamp}.json")
            
            import shutil
            shutil.copy2(self.resume_path, backup_path)
            
            logger.info(f"Resume backed up to {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise FileOperationError(f"Failed to backup resume: {e}")
    
    # RxResume Integration Methods
    
    async def create_rxresume_resume(
        self, 
        job_id: str = None, 
        resume_name: str = None,
        template_override: str = None,
        with_sample_data: bool = False
    ) -> str:
        """
        Create a new resume on RxResume.
        
        Args:
            job_id: Optional job ID to associate resume with
            resume_name: Custom name (auto-generated if None)
            template_override: Manual template selection
            with_sample_data: Initialize with RxResume sample data
            
        Returns:
            str: RxResume resume ID
            
        Raises:
            RxResumeAPIError: For API-related errors
            ProfileException: For resume loading errors
        """
        try:
            # Load current local resume
            local_resume = await self.get_resume()
            
            # Generate resume name if not provided
            if not resume_name:
                if job_id:
                    job_title, company = self._get_job_details(job_id)
                    resume_name = self.transformer.generate_resume_name(job_title, company)
                else:
                    resume_name = f"Resume - {local_resume.name}"
            
            # Generate unique slug
            slug = self.transformer.generate_unique_slug(resume_name)
            
            # Determine template
            template = self.transformer.map_template(local_resume, template_override)
            
            # Transform resume data for RxResume
            rxresume_data = self.transformer.local_to_rxresume(local_resume)
            
            # Create on RxResume
            rxresume_id = await self.rxresume_client.create_resume(
                name=resume_name,
                slug=slug,
                tags=local_resume.tags,
                with_sample_data=with_sample_data
            )
            
            # Update with our resume data if not using sample data
            if not with_sample_data:
                await self.rxresume_client.update_resume(
                    resume_id=rxresume_id,
                    update_data={
                        "data": rxresume_data,
                        "isPublic": local_resume.isPublic
                    }
                )
            
            # Store association in database if job_id provided
            if job_id:
                self._create_resume_job_record(
                    job_id=job_id,
                    rxresume_id=rxresume_id,
                    resume_name=resume_name,
                    template=template,
                    user_template_override=template_override
                )
            
            logger.info(f"Successfully created RxResume resume: {rxresume_id}")
            return rxresume_id
            
        except (RxResumeAPIError, RxResumeAuthenticationError, RxResumeValidationError, 
                RxResumeNotFoundError, RxResumeNetworkError, RxResumeSlugExistsError) as e:
            logger.error(f"RxResume API error creating resume: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error creating RxResume resume: {e}")
            raise ProfileException(f"Failed to create resume on RxResume: {e}")
    
    async def update_rxresume_resume(
        self, 
        rxresume_id: str, 
        resume_data: Dict[str, Any] = None,
        template_override: str = None
    ) -> Dict[str, Any]:
        """
        Update existing RxResume resume.
        
        Args:
            rxresume_id: RxResume resume identifier
            resume_data: Custom data (uses local resume if None)
            template_override: Change template
            
        Returns:
            Dict[str, Any]: Updated resume object from RxResume
            
        Raises:
            RxResumeAPIError: For API-related errors
        """
        try:
            # Load data to update
            if resume_data:
                # Use provided data
                validated_resume = Resume(**resume_data)
            else:
                # Use current local resume
                validated_resume = await self.get_resume()
            
            # Transform to RxResume format
            rxresume_data = self.transformer.local_to_rxresume(validated_resume)
            
            # Prepare update payload
            update_payload = {
                "data": rxresume_data,
                "isPublic": validated_resume.isPublic
            }
            
            # Add template if specified
            if template_override:
                # Note: Template changes might need to be in the metadata
                rxresume_data["metadata"]["template"] = template_override
                update_payload["data"] = rxresume_data
            
            # Update on RxResume
            updated_resume = await self.rxresume_client.update_resume(
                resume_id=rxresume_id,
                update_data=update_payload
            )
            
            # Update database sync status
            self._update_resume_job_sync_status_by_rxresume_id(rxresume_id, "synced")
            
            logger.info(f"Successfully updated RxResume resume: {rxresume_id}")
            return updated_resume
            
        except (RxResumeAPIError, RxResumeAuthenticationError, RxResumeValidationError, 
                RxResumeNotFoundError, RxResumeNetworkError) as e:
            logger.error(f"RxResume API error updating resume {rxresume_id}: {e}")
            # Mark as failed in database
            self._update_resume_job_sync_status_by_rxresume_id(rxresume_id, "failed")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error updating RxResume resume {rxresume_id}: {e}")
            self._update_resume_job_sync_status_by_rxresume_id(rxresume_id, "error")
            raise ProfileException(f"Failed to update resume on RxResume: {e}")
    
    async def delete_rxresume_resume(self, rxresume_id: str) -> bool:
        """
        Delete a resume on RxResume and remove local association.
        
        Args:
            rxresume_id: RxResume resume identifier
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            RxResumeAPIError: For API-related errors
        """
        try:
            # Delete from RxResume
            success = await self.rxresume_client.delete_resume(rxresume_id)
            
            if success:
                # Remove from local database
                self._delete_resume_job_record_by_rxresume_id(rxresume_id)
                logger.info(f"Successfully deleted RxResume resume and local record: {rxresume_id}")
            
            return success
            
        except (RxResumeAPIError, RxResumeAuthenticationError, 
                RxResumeNotFoundError, RxResumeNetworkError) as e:
            logger.error(f"RxResume API error deleting resume {rxresume_id}: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error deleting RxResume resume {rxresume_id}: {e}")
            raise ProfileException(f"Failed to delete resume on RxResume: {e}")
    
    async def sync_resume_to_job(self, job_id: str, template_override: str = None) -> str:
        """
        Create or update resume for specific job application.
        
        Args:
            job_id: Job posting identifier
            template_override: Manual template selection
            
        Returns:
            str: RxResume resume ID (existing or newly created)
        """
        try:
            # Check if resume already exists for this job
            existing_record = self._get_resume_job_by_job_id(job_id)
            
            if existing_record:
                # Update existing resume
                await self.update_rxresume_resume(
                    rxresume_id=existing_record.rxresume_id,
                    template_override=template_override
                )
                return existing_record.rxresume_id
            else:
                # Create new resume
                return await self.create_rxresume_resume(
                    job_id=job_id,
                    template_override=template_override
                )
                
        except Exception as e:
            logger.error(f"Failed to sync resume for job {job_id}: {e}")
            raise
    
    async def get_resume_for_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get resume details for a specific job."""
        try:
            record = self._get_resume_job_by_job_id(job_id)
            if record:
                return {
                    "id": record.id,
                    "job_id": record.job_id,
                    "rxresume_id": record.rxresume_id,
                    "resume_name": record.resume_name,
                    "created_at": record.created_at,
                    "updated_at": record.updated_at,
                    "sync_status": record.sync_status,
                    "template": record.template,
                    "user_template_override": record.user_template_override
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get resume for job {job_id}: {e}")
            return None
    
    async def list_job_resumes(self) -> List[Dict[str, Any]]:
        """List all job-resume associations with sync status."""
        try:
            records = self._get_all_resume_jobs()
            return [
                {
                    "id": record.id,
                    "job_id": record.job_id,
                    "rxresume_id": record.rxresume_id,
                    "resume_name": record.resume_name,
                    "created_at": record.created_at,
                    "updated_at": record.updated_at,
                    "sync_status": record.sync_status,
                    "template": record.template,
                    "user_template_override": record.user_template_override
                }
                for record in records
            ]
        except Exception as e:
            logger.error(f"Failed to list job resumes: {e}")
            return []
    
    async def bulk_sync_resumes(self, request: BulkSyncRequest) -> BulkSyncResponse:
        """
        Sync multiple resumes to RxResume in bulk.
        
        Args:
            request: Bulk sync configuration
            
        Returns:
            BulkSyncResponse: Results of bulk operation
        """
        response = BulkSyncResponse(
            total_jobs=0,
            successful=0,
            failed=0,
            errors=[],
            created_resumes=[],
            updated_resumes=[]
        )
        
        try:
            # Get jobs to sync
            if request.job_ids:
                job_ids = request.job_ids
            else:
                # Get all jobs (you'll need to implement this based on your job model)
                job_ids = self._get_all_job_ids()
            
            response.total_jobs = len(job_ids)
            
            for job_id in job_ids:
                try:
                    # Check if already synced and force_update is False
                    existing_record = self._get_resume_job_by_job_id(job_id)
                    if existing_record and not request.force_update:
                        if existing_record.sync_status == "synced":
                            response.successful += 1
                            response.updated_resumes.append(existing_record.rxresume_id)
                            continue
                    
                    # Sync resume for job
                    rxresume_id = await self.sync_resume_to_job(
                        job_id=job_id,
                        template_override=request.template_override
                    )
                    
                    response.successful += 1
                    if existing_record:
                        response.updated_resumes.append(rxresume_id)
                    else:
                        response.created_resumes.append(rxresume_id)
                    
                except Exception as e:
                    response.failed += 1
                    response.errors.append({
                        "job_id": job_id,
                        "error": str(e)
                    })
                    logger.error(f"Failed to sync resume for job {job_id}: {e}")
            
            logger.info(f"Bulk sync completed: {response.successful}/{response.total_jobs} successful")
            return response
            
        except Exception as e:
            logger.error(f"Bulk sync operation failed: {e}")
            raise ProfileException(f"Bulk sync failed: {e}")
    
    async def get_available_templates(self) -> List[Dict[str, Any]]:
        """Fetch available templates from RxResume."""
        try:
            templates = await self.rxresume_client.get_templates()
            return [
                {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "category": template.category,
                    "preview_url": template.preview_url
                }
                for template in templates
            ]
        except Exception as e:
            logger.error(f"Failed to fetch templates: {e}")
            return []
    
    # Internal helper methods
    
    async def _auto_sync_to_rxresume(self, job_id: str) -> bool:
        """Background sync with comprehensive error handling."""
        try:
            existing = await self.get_resume_for_job(job_id)
            if existing:
                await self.update_rxresume_resume(existing['rxresume_id'])
            else:
                await self.sync_resume_to_job(job_id)
            return True
        except Exception as e:
            logger.error(f"RxResume sync failed for job {job_id}: {e}")
            # Update database sync_status to 'failed' if record exists
            if existing:
                self._update_resume_job_sync_status(job_id, "failed")
            return False
    
    def _get_job_details(self, job_id: str) -> tuple[str, str]:
        """Get job title and company from database."""
        try:
            with SessionLocal() as db:
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    return str(job.title or "Position"), str(job.company or "Company")
                return "Position", "Company"
        except Exception as e:
            logger.warning(f"Failed to get job details for {job_id}: {e}")
            return "Position", "Company"
    
    # Database DAO methods
    
    def _create_resume_job_record(
        self, 
        job_id: str, 
        rxresume_id: str, 
        resume_name: str, 
        template: str,
        user_template_override: str = None
    ) -> None:
        """Insert new resume-job association."""
        try:
            with SessionLocal() as db:
                record = ResumeJob(
                    job_id=job_id,
                    rxresume_id=rxresume_id,
                    resume_name=resume_name,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    sync_status="synced",
                    template=template,
                    user_template_override=user_template_override
                )
                db.add(record)
                db.commit()
                logger.debug(f"Created resume-job record: {job_id} -> {rxresume_id}")
        except Exception as e:
            logger.error(f"Failed to create resume-job record: {e}")
            raise FileOperationError(f"Database error: {e}")
    
    def _update_resume_job_sync_status(self, job_id: str, status: str) -> None:
        """Update sync status for job resume."""
        try:
            with SessionLocal() as db:
                record = db.query(ResumeJob).filter(ResumeJob.job_id == job_id).first()
                if record:
                    record.sync_status = status
                    record.updated_at = datetime.now().isoformat()
                    db.commit()
                    logger.debug(f"Updated sync status for job {job_id}: {status}")
        except Exception as e:
            logger.error(f"Failed to update sync status: {e}")
    
    def _update_resume_job_sync_status_by_rxresume_id(self, rxresume_id: str, status: str) -> None:
        """Update sync status by RxResume ID."""
        try:
            with SessionLocal() as db:
                record = db.query(ResumeJob).filter(ResumeJob.rxresume_id == rxresume_id).first()
                if record:
                    record.sync_status = status
                    record.updated_at = datetime.now().isoformat()
                    db.commit()
                    logger.debug(f"Updated sync status for resume {rxresume_id}: {status}")
        except Exception as e:
            logger.error(f"Failed to update sync status: {e}")
    
    def _get_resume_job_by_job_id(self, job_id: str) -> Optional[ResumeJob]:
        """Fetch resume association for job."""
        try:
            with SessionLocal() as db:
                return db.query(ResumeJob).filter(ResumeJob.job_id == job_id).first()
        except Exception as e:
            logger.error(f"Failed to get resume-job record: {e}")
            return None
    
    def _get_all_resume_jobs(self) -> List[ResumeJob]:
        """Fetch all resume-job associations."""
        try:
            with SessionLocal() as db:
                return db.query(ResumeJob).all()
        except Exception as e:
            logger.error(f"Failed to get all resume-job records: {e}")
            return []
    
    def _delete_resume_job_record_by_rxresume_id(self, rxresume_id: str) -> None:
        """Delete resume-job association by RxResume ID."""
        try:
            with SessionLocal() as db:
                record = db.query(ResumeJob).filter(ResumeJob.rxresume_id == rxresume_id).first()
                if record:
                    db.delete(record)
                    db.commit()
                    logger.debug(f"Deleted resume-job record for resume {rxresume_id}")
        except Exception as e:
            logger.error(f"Failed to delete resume-job record: {e}")
    
    def _get_all_job_ids(self) -> List[str]:
        """Get all job IDs from database."""
        try:
            with SessionLocal() as db:
                jobs = db.query(Job.id).all()
                return [job.id for job in jobs]
        except Exception as e:
            logger.error(f"Failed to get job IDs: {e}")
            return []
