"""
Profile service for the PlsFindMeAJob application.
Contains all business logic for profile operations.
"""
import logging
from typing import Dict, Any
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import (
    ProfileException,
    ProfileValidationError,
    ProfileCorruptedError,
    FileOperationError,
    ProfilePermissionError
)
from app.models.schemas import Profile, SaveResponse, Basics
from app.utils.file_handler import ProfileFileHandler

logger = logging.getLogger(__name__)


class ProfileService:
    """Service class for handling all profile-related business logic."""
    
    def __init__(self):
        """Initialize ProfileService with file handler."""
        self.file_handler = ProfileFileHandler(settings.PROFILE_PATH)
    
    async def get_profile(self) -> Profile:
        """
        Retrieve user profile with proper validation and error handling.
        
        Returns:
            Profile: Validated profile data
            
        Raises:
            ProfileException: For profile-related errors
            FileOperationError: For file I/O errors
        """
        try:
            # Load profile data from file
            profile_data = self.file_handler.load_profile_data()
            
            # Validate the loaded data
            try:
                validated_profile = Profile(**profile_data)
                logger.debug("Profile loaded and validated successfully")
                return validated_profile
                
            except ValidationError as e:
                # If validation fails, return empty profile
                logger.warning(f"Profile validation failed: {e}")
                return self._get_empty_profile()
                
        except ProfileCorruptedError as e:
            logger.error(f"Profile file corrupted: {e}")
            raise ProfileException(f"Profile data is corrupted: {e}")
            
        except FileOperationError as e:
            logger.error(f"File operation failed: {e}")
            raise ProfileException(f"Failed to load profile: {e}")
            
        except Exception as e:
            logger.error(f"Unexpected error loading profile: {e}")
            raise ProfileException(f"Unexpected error loading profile: {e}")
    
    async def save_profile(self, profile_data: Dict[str, Any]) -> SaveResponse:
        """
        Save user profile with validation and error handling.
        
        Args:
            profile_data: Raw profile data dictionary
            
        Returns:
            SaveResponse: Result of save operation
            
        Raises:
            ProfileValidationError: For validation errors
            ProfilePermissionError: For permission errors
            ProfileException: For other profile-related errors
        """
        try:
            # Validate the incoming data
            try:
                validated_profile = Profile(**profile_data)
                logger.debug("Profile data validated successfully")
                
            except ValidationError as e:
                # Extract field-specific errors
                errors = {}
                for error in e.errors():
                    field = '.'.join(str(loc) for loc in error['loc'])
                    errors[field] = error['msg']
                
                logger.warning(f"Profile validation failed: {errors}")
                raise ProfileValidationError(
                    "Validation failed", 
                    validation_errors=errors
                )
            
            # Save the validated profile
            self.file_handler.save_profile_data(validated_profile.dict())
            
            logger.info("Profile saved successfully")
            return SaveResponse(
                success=True,
                message="Profile saved successfully!"
            )
            
        except ProfileValidationError:
            # Re-raise validation errors
            raise
            
        except ProfilePermissionError as e:
            logger.error(f"Permission error saving profile: {e}")
            raise ProfileException(f"Permission denied: Cannot save profile - {e}")
            
        except FileOperationError as e:
            logger.error(f"File operation failed: {e}")
            raise ProfileException(f"Failed to save profile: {e}")
            
        except Exception as e:
            logger.error(f"Unexpected error saving profile: {e}")
            raise ProfileException(f"Unexpected error saving profile: {e}")
    
    def _get_empty_profile(self) -> Profile:
        """
        Create an empty profile with default values.
        
        Returns:
            Profile: Empty profile instance
        """
        return Profile(
            basics=Basics(name="", email="", phone=""),
            experiences=[],
            education=[],
            skills=[],
            projects=[]
        )
    
    async def validate_profile_data(self, profile_data: Dict[str, Any]) -> Profile:
        """
        Validate profile data without saving.
        
        Args:
            profile_data: Raw profile data dictionary
            
        Returns:
            Profile: Validated profile instance
            
        Raises:
            ProfileValidationError: If validation fails
        """
        try:
            validated_profile = Profile(**profile_data)
            logger.debug("Profile data validation successful")
            return validated_profile
            
        except ValidationError as e:
            errors = {}
            for error in e.errors():
                field = '.'.join(str(loc) for loc in error['loc'])
                errors[field] = error['msg']
            
            logger.warning(f"Profile validation failed: {errors}")
            raise ProfileValidationError(
                "Profile validation failed",
                validation_errors=errors
            )