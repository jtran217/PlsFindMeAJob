"""
Profile API routes for the PlsFindMeAJob application.
Provides clean, thin route handlers focused only on HTTP concerns.
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import (
    ProfileException,
    ProfileValidationError,
    ProfilePermissionError
)
from app.models.schemas import Profile, SaveResponse
from app.services.profile_service import ProfileService

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter()

# Initialize service
profile_service = ProfileService()


@router.get("/profile", response_model=Profile)
async def get_profile():
    """
    Retrieve user profile data.
    
    Returns:
        Profile: User profile with all sections
        
    Raises:
        HTTPException: For various error conditions
    """
    try:
        profile = await profile_service.get_profile()
        return profile
        
    except ProfileException as e:
        logger.error(f"Profile service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error getting profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load profile"
        )


@router.post("/profile", response_model=SaveResponse)
async def save_profile(profile_data: Dict[str, Any]):
    """
    Save user profile data with validation.
    
    Args:
        profile_data: Profile data dictionary
        
    Returns:
        SaveResponse: Result of save operation
        
    Raises:
        HTTPException: For validation or save errors
    """
    try:
        result = await profile_service.save_profile(profile_data)
        return result
        
    except ProfileValidationError as e:
        logger.warning(f"Profile validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "success": False,
                "message": e.message,
                "errors": e.validation_errors
            }
        )
    except ProfilePermissionError as e:
        logger.error(f"Permission error saving profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Permission denied: Cannot save profile"
            }
        )
    except ProfileException as e:
        logger.error(f"Profile service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error saving profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Failed to save profile"
            }
        )