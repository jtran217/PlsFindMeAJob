"""
File handling utilities for the PlsFindMeAJob application.
Provides abstraction for file I/O operations with proper error handling.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.exceptions import (
    FileOperationError, 
    ProfileCorruptedError, 
    ProfilePermissionError
)

logger = logging.getLogger(__name__)


class FileHandler:
    """Generic file handler with comprehensive error handling."""
    
    @staticmethod
    def ensure_directory(file_path: Path) -> None:
        """
        Ensure the parent directory of a file exists.
        
        Args:
            file_path: Path to the file
            
        Raises:
            FileOperationError: If directory creation fails
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {file_path.parent}")
        except PermissionError as e:
            raise FileOperationError(f"Permission denied creating directory: {e}")
        except Exception as e:
            raise FileOperationError(f"Failed to create directory: {e}")
    
    @staticmethod
    def read_json(file_path: Path) -> Dict[str, Any]:
        """
        Read JSON data from file with error handling.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dict containing the JSON data
            
        Raises:
            FileOperationError: If file cannot be read
            ProfileCorruptedError: If JSON is malformed
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            with open(file_path, "r") as f:
                data = json.load(f)
            
            logger.debug(f"Successfully read JSON from {file_path}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
            raise ProfileCorruptedError(f"Corrupted JSON in {file_path}: {e}")
        except PermissionError as e:
            logger.error(f"Permission error reading {file_path}: {e}")
            raise ProfilePermissionError(f"Permission denied reading {file_path}")
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            raise FileOperationError(f"Failed to read {file_path}: {e}")
    
    @staticmethod
    def write_json(file_path: Path, data: Dict[str, Any], indent: int = 2) -> None:
        """
        Write JSON data to file with error handling.
        
        Args:
            file_path: Path to JSON file
            data: Data to write
            indent: JSON indentation level
            
        Raises:
            FileOperationError: If file cannot be written
            ProfilePermissionError: If permission denied
        """
        try:
            FileHandler.ensure_directory(file_path)
            
            with open(file_path, "w") as f:
                json.dump(data, f, indent=indent)
            
            logger.debug(f"Successfully wrote JSON to {file_path}")
            
        except PermissionError as e:
            logger.error(f"Permission error writing {file_path}: {e}")
            raise ProfilePermissionError(f"Permission denied writing {file_path}")
        except Exception as e:
            logger.error(f"Error writing {file_path}: {e}")
            raise FileOperationError(f"Failed to write {file_path}: {e}")
    
    @staticmethod
    def file_exists(file_path: Path) -> bool:
        """Check if file exists."""
        return file_path.exists()


class ProfileFileHandler:
    """Specialized file handler for profile operations."""
    
    def __init__(self, profile_path: Path):
        """
        Initialize with profile file path.
        
        Args:
            profile_path: Path to profile JSON file
        """
        self.profile_path = profile_path
        self.file_handler = FileHandler()
    
    def load_profile_data(self) -> Dict[str, Any]:
        """
        Load profile data from file or create empty profile if not found.
        
        Returns:
            Dict containing profile data
            
        Raises:
            ProfileCorruptedError: If profile file is corrupted
            FileOperationError: If file operations fail
        """
        try:
            if not self.file_handler.file_exists(self.profile_path):
                logger.info("Profile file not found, creating empty profile")
                empty_profile = self._get_empty_profile_data()
                self.save_profile_data(empty_profile)
                return empty_profile
            
            return self.file_handler.read_json(self.profile_path)
            
        except (ProfileCorruptedError, FileOperationError):
            # Re-raise profile-specific errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading profile: {e}")
            raise FileOperationError(f"Failed to load profile: {e}")
    
    def save_profile_data(self, profile_data: Dict[str, Any]) -> None:
        """
        Save profile data to file.
        
        Args:
            profile_data: Profile data dictionary
            
        Raises:
            ProfilePermissionError: If permission denied
            FileOperationError: If save operation fails
        """
        try:
            self.file_handler.write_json(self.profile_path, profile_data)
            logger.info("Profile data saved successfully")
        except (ProfilePermissionError, FileOperationError):
            # Re-raise specific errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving profile: {e}")
            raise FileOperationError(f"Failed to save profile: {e}")
    
    def _get_empty_profile_data(self) -> Dict[str, Any]:
        """Get empty profile data structure."""
        return {
            "basics": {
                "name": "",
                "email": "",
                "phone": "",
                "linkedin": "",
                "github": ""
            },
            "experiences": [],
            "education": [],
            "skills": [],
            "projects": []
        }