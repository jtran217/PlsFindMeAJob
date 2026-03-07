"""
Resume service for the enhanced resume system.
Handles all operations for the new resume optimization format.
"""
import logging
from typing import Dict, Any, Optional
from pydantic import ValidationError
import json
from pathlib import Path
from datetime import datetime

from app.core.config import settings
from app.core.exceptions import (
    ProfileException,
    ProfileValidationError,
    ProfileCorruptedError,
    FileOperationError,
    ProfilePermissionError
)
from app.models.resume_schemas import Resume, ResumeResponse, ResumeSaveResponse, ResumeData, EnhancedBasics
from app.utils.profile_migration import ProfileMigrator
from app.utils.file_handler import ProfileFileHandler

logger = logging.getLogger(__name__)


class ResumeService:
    """Service class for handling all resume-related business logic."""
    
    def __init__(self):
        """Initialize ResumeService with file handler and migrator."""
        self.file_handler = ProfileFileHandler(settings.PROFILE_PATH)
        self.migrator = ProfileMigrator()
        self.resume_path = Path(settings.PROFILE_PATH).parent / "resume.json"
    
    async def get_resume(self, auto_migrate: bool = True) -> Resume:
        """
        Retrieve user resume with proper validation and migration support.
        
        Args:
            auto_migrate: Whether to automatically migrate legacy profiles
            
        Returns:
            Resume: Validated resume data
            
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
                    logger.warning(f"Resume file corrupted, attempting migration: {e}")
                    if auto_migrate:
                        return await self._migrate_and_save()
                    raise ProfileCorruptedError(f"Resume file corrupted: {e}")
            
            elif auto_migrate:
                logger.info("No resume file found, attempting migration from legacy profile")
                return await self._migrate_and_save()
            
            else:
                logger.info("No resume or profile data found, returning default")
                return self._get_default_resume()
                
        except FileOperationError as e:
            logger.error(f"File operation failed: {e}")
            raise ProfileException(f"Failed to load resume: {e}")
            
        except Exception as e:
            logger.error(f"Unexpected error loading resume: {e}")
            raise ProfileException(f"Unexpected error loading resume: {e}")
    
    async def save_resume(self, resume_data: Dict[str, Any]) -> ResumeSaveResponse:
        """
        Save user resume with validation and error handling.
        
        Args:
            resume_data: Raw resume data dictionary
            
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
            
            try:
                legacy_data = self.migrator.migrate_resume_to_legacy(validated_resume)
                self.file_handler.save_profile_data(legacy_data)
                logger.debug("Legacy profile backup saved")
            except Exception as e:
                logger.warning(f"Failed to save legacy backup: {e}")
            
            logger.info("Resume saved successfully")
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
    
    async def migrate_legacy_profile(self) -> Resume:
        """
        Manually migrate legacy profile to resume format.
        
        Returns:
            Resume: Migrated resume
            
        Raises:
            ProfileException: If migration fails
        """
        try:
            return await self._migrate_and_save()
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise ProfileException(f"Failed to migrate profile: {e}")
    
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
    
    async def _migrate_and_save(self) -> Resume:
        """Migrate legacy profile to resume format and save."""
        try:
            legacy_data = self.file_handler.load_profile_data()
            migrated_resume = self.migrator.migrate_legacy_to_resume(legacy_data)
            self._save_resume_data(migrated_resume.dict())
            
            logger.info(f"Successfully migrated and saved resume for {migrated_resume.data.basics.name}")
            return migrated_resume
            
        except Exception as e:
            logger.error(f"Migration and save failed: {e}")
            raise ProfileException(f"Failed to migrate profile: {e}")
    
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
