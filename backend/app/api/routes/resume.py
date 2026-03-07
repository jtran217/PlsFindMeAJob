"""
Resume API routes for the enhanced resume system (v2).
Provides endpoints for the new resume optimization format.
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import (
    ProfileException,
    ProfileValidationError,
    ProfilePermissionError
)
from app.models.resume_schemas import Resume, ResumeResponse, ResumeSaveResponse
from app.services.resume_service import ResumeService

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter()

# Initialize service
resume_service = ResumeService()


@router.get("/resume", response_model=Resume)
async def get_resume():
    """
    Retrieve user resume data in the enhanced format.
    
    Returns:
        Resume: Complete resume data or default if not found
        
    Raises:
        HTTPException: For various error conditions
    """
    try:
        resume = await resume_service.get_resume()
        return resume
        
    except ProfileException as e:
        logger.error(f"Resume service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error getting resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load resume"
        )


@router.post("/resume", response_model=ResumeSaveResponse)
async def save_resume(resume_data: Dict[str, Any]):
    """
    Save user resume data with validation.
    
    Args:
        resume_data: Complete resume data dictionary
        
    Returns:
        ResumeSaveResponse: Result of save operation
        
    Raises:
        HTTPException: For validation or save errors
    """
    try:
        result = await resume_service.save_resume(resume_data)
        return result
        
    except ProfileValidationError as e:
        logger.warning(f"Resume validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "success": False,
                "message": e.message,
                "errors": e.validation_errors
            }
        )
    except ProfilePermissionError as e:
        logger.error(f"Permission error saving resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Permission denied: Cannot save resume"
            }
        )
    except ProfileException as e:
        logger.error(f"Resume service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error saving resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Failed to save resume"
            }
        )


@router.post("/resume/validate", response_model=ResumeResponse)
async def validate_resume(resume_data: Dict[str, Any]):
    """
    Validate resume data without saving.
    
    Args:
        resume_data: Resume data to validate
        
    Returns:
        ResumeResponse: Validation result with validated data
        
    Raises:
        HTTPException: For validation errors
    """
    try:
        validated_resume = await resume_service.validate_resume_data(resume_data)
        return ResumeResponse(
            success=True,
            message="Resume data is valid",
            data=validated_resume
        )
        
    except ProfileValidationError as e:
        logger.warning(f"Resume validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "success": False,
                "message": e.message,
                "errors": e.validation_errors
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error validating resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Validation failed"
            }
        )


@router.get("/resume/backup", response_model=Dict[str, str])
async def backup_resume():
    """
    Create a backup of the current resume.
    
    Returns:
        Dict: Backup file information
        
    Raises:
        HTTPException: If backup fails
    """
    try:
        backup_path = resume_service.backup_resume()
        return {
            "success": True,
            "message": "Resume backed up successfully",
            "backup_path": backup_path
        }
        
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backup failed: {e}"
        )