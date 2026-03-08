"""
Custom exception classes for the PlsFindMeAJob application.
Provides specific exception types for better error handling and debugging.
"""
from typing import Dict, Any, Optional
import logging


class PlsFindMeAJobException(Exception):
    """
    Base exception for all application-specific errors.
    
    Provides structured error handling with message and optional details.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
        
        # Log the exception for debugging
        logging.getLogger(__name__).debug(f"{self.__class__.__name__}: {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class ProfileException(PlsFindMeAJobException):
    """
    Base exception for profile-related operations.
    
    Used for general profile loading, saving, and processing errors.
    """
    
    def __init__(self, message: str, operation: str = "unknown", details: Optional[Dict[str, Any]] = None):
        self.operation = operation
        enhanced_details = details or {}
        enhanced_details["operation"] = operation
        super().__init__(message, enhanced_details)


class FileOperationError(PlsFindMeAJobException):
    """
    Exception raised when file I/O operations fail.
    
    Includes file path and operation type for better debugging.
    """
    
    def __init__(self, message: str, file_path: Optional[str] = None, operation: str = "unknown"):
        self.file_path = file_path
        self.operation = operation
        details = {
            "file_path": file_path,
            "operation": operation
        }
        super().__init__(message, details)


class ValidationError(PlsFindMeAJobException):
    """
    Exception raised when input validation fails.
    
    Used for API parameter validation and business rule enforcement.
    """
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        self.field = field
        self.value = value
        details = {}
        if field is not None:
            details["field"] = field
        if value is not None:
            details["invalid_value"] = str(value)
        super().__init__(message, details)


class ProfileValidationError(ProfileException):
    """
    Exception raised when profile data validation fails.
    
    Provides detailed validation errors for form feedback.
    """
    
    def __init__(self, message: str, validation_errors: Dict[str, str], operation: str = "validation"):
        self.validation_errors = validation_errors
        details = {"validation_errors": validation_errors}
        super().__init__(message, operation, details)
    
    def get_field_errors(self) -> Dict[str, str]:
        """Get field-specific validation errors for form display."""
        return self.validation_errors


class ProfilePermissionError(ProfileException):
    """
    Exception raised when profile operations are denied due to permissions.
    
    Tracks permission type and attempted operation for security auditing.
    """
    
    def __init__(self, message: str, operation: str = "unknown", permission_type: str = "file_access"):
        self.permission_type = permission_type
        details = {"permission_type": permission_type}
        super().__init__(message, operation, details)


class ProfileCorruptedError(ProfileException):
    """
    Exception raised when profile data is corrupted or malformed.
    
    Includes corruption details for data recovery attempts.
    """
    
    def __init__(self, message: str, file_path: Optional[str] = None, corruption_type: str = "unknown"):
        self.file_path = file_path
        self.corruption_type = corruption_type
        details = {
            "file_path": file_path,
            "corruption_type": corruption_type
        }
        super().__init__(message, "data_validation", details)


# RxResume API Integration Exceptions

class RxResumeAPIError(PlsFindMeAJobException):
    """
    Base exception for RxResume API errors.
    
    Provides structured error handling for all RxResume API interactions.
    """
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        self.status_code = status_code
        self.response_data = response_data or {}
        details = {
            "status_code": status_code,
            "response_data": response_data
        }
        super().__init__(message, details)


class RxResumeAuthenticationError(RxResumeAPIError):
    """
    Exception raised when RxResume API authentication fails.
    
    Indicates invalid API key or authentication issues.
    """
    
    def __init__(self, message: str = "RxResume API authentication failed", api_key_provided: bool = False):
        self.api_key_provided = api_key_provided
        details = {"api_key_provided": api_key_provided}
        super().__init__(message, 401, details)


class RxResumeValidationError(RxResumeAPIError):
    """
    Exception raised when RxResume API validation fails.
    
    Indicates data format or content validation errors on RxResume side.
    """
    
    def __init__(self, message: str, validation_errors: Optional[Dict[str, Any]] = None):
        self.validation_errors = validation_errors or {}
        details = {"validation_errors": validation_errors}
        super().__init__(message, 400, details)


class RxResumeNotFoundError(RxResumeAPIError):
    """
    Exception raised when a resume ID is not found on RxResume.
    
    Indicates the resume may have been deleted or ID is incorrect.
    """
    
    def __init__(self, message: str, resume_id: Optional[str] = None):
        self.resume_id = resume_id
        details = {"resume_id": resume_id}
        super().__init__(message, 404, details)


class RxResumeNetworkError(RxResumeAPIError):
    """
    Exception raised when network/connection issues occur with RxResume API.
    
    Includes timeout, connection, and other network-related errors.
    """
    
    def __init__(self, message: str, error_type: str = "connection", timeout_seconds: Optional[float] = None):
        self.error_type = error_type
        self.timeout_seconds = timeout_seconds
        details = {
            "error_type": error_type,
            "timeout_seconds": timeout_seconds
        }
        super().__init__(message, None, details)


class RxResumeSlugExistsError(RxResumeAPIError):
    """
    Exception raised when a resume slug already exists on RxResume.
    
    Indicates slug conflict and need for unique slug generation.
    """
    
    def __init__(self, message: str, slug: Optional[str] = None):
        self.slug = slug
        details = {"slug": slug}
        super().__init__(message, 400, details)

