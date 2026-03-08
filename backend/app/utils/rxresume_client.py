"""
RxResume API HTTP client for resume integration.
Handles all HTTP communications with the RxResume API.
"""
import httpx
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.exceptions import (
    RxResumeAPIError,
    RxResumeAuthenticationError,
    RxResumeValidationError,
    RxResumeNotFoundError,
    RxResumeNetworkError,
    RxResumeSlugExistsError
)
from app.models.rxresume_schemas import (
    RxResumeCreateRequest,
    RxResumeUpdateRequest,
    RxResumeCreateResponse,
    RxResumeUpdateResponse,
    RxResumeErrorResponse,
    RxResumeTemplate,
    RxResumeTemplateListResponse
)

logger = logging.getLogger(__name__)


class RxResumeClient:
    """
    HTTP client for RxResume API integration.
    
    Provides methods for creating, updating, and managing resumes on RxResume,
    with comprehensive error handling and response validation.
    """
    
    def __init__(self):
        self.api_key = settings.rxresume_api_key
        self.base_url = settings.rxresume_base_url.rstrip('/')
        self.timeout = 30.0  
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": f"PlsFindMeAJob/1.0.0 (+https://github.com/jtran217/PlsFindMeAJob)"
        }
        if not self.api_key:
            logger.warning("RxResume API key not configured - API calls will fail")
    
    async def create_resume(
        self, 
        name: str, 
        slug: str, 
        tags: List[str], 
        with_sample_data: bool = False
    ) -> str:
        """
        Create a new resume on RxResume.
        
        Args:
            name: The name of the resume
            slug: URL-friendly slug for the resume
            tags: List of tags to categorize the resume
            with_sample_data: Whether to initialize with sample data
            
        Returns:
            str: The ID of the newly created resume
            
        Raises:
            RxResumeAuthenticationError: If API key is invalid
            RxResumeValidationError: If request data is invalid
            RxResumeSlugExistsError: If slug already exists
            RxResumeNetworkError: For network/connection issues
            RxResumeAPIError: For other API errors
        """
        if not self.api_key:
            raise RxResumeAuthenticationError("RxResume API key not configured", api_key_provided=False)
        
        try:
            request_data = RxResumeCreateRequest(
                name=name,
                slug=slug,
                tags=tags,
                withSampleData=with_sample_data
            )
        except Exception as e:
            raise RxResumeValidationError(f"Invalid request data: {e}")
        
        url = f"{self.base_url}/resumes"
        payload = request_data.dict()
        
        logger.debug(f"Creating resume on RxResume: {name} (slug: {slug})")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers
                )
                self._handle_api_error(response, operation="create_resume")
                if response.status_code == 200:
                    resume_id = response.json()
                    if isinstance(resume_id, str):
                        logger.info(f"Successfully created resume '{name}' with ID: {resume_id}")
                        return resume_id
                    else:
                        raise RxResumeAPIError(f"Unexpected response format: {resume_id}")
                else:
                    raise RxResumeAPIError(f"Unexpected status code: {response.status_code}")
        except httpx.TimeoutException as e:
            raise RxResumeNetworkError(
                f"Request timeout while creating resume: {e}",
                error_type="timeout",
                timeout_seconds=self.timeout
            )
        except httpx.ConnectError as e:
            raise RxResumeNetworkError(
                f"Connection error while creating resume: {e}",
                error_type="connection"
            )
        except Exception as e:
            if isinstance(e, (RxResumeAPIError, RxResumeAuthenticationError, RxResumeValidationError)):
                raise
            raise RxResumeNetworkError(f"Unexpected error during resume creation: {e}")
    async def update_resume(
        self, 
        resume_id: str, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing resume on RxResume.
        
        Args:
            resume_id: The ID of the resume to update
            update_data: Dictionary with fields to update
            
        Returns:
            Dict[str, Any]: Full updated resume object
            
        Raises:
            RxResumeAuthenticationError: If API key is invalid
            RxResumeNotFoundError: If resume ID doesn't exist
            RxResumeValidationError: If update data is invalid
            RxResumeNetworkError: For network/connection issues
            RxResumeAPIError: For other API errors
        """
        if not self.api_key:
            raise RxResumeAuthenticationError("RxResume API key not configured", api_key_provided=False)
        try:
            request_data = RxResumeUpdateRequest(**update_data)
        except Exception as e:
            raise RxResumeValidationError(f"Invalid update data: {e}")
        url = f"{self.base_url}/resumes/{resume_id}"
        payload = request_data.dict(exclude_none=True)  
        logger.debug(f"Updating resume {resume_id} on RxResume")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(
                    url,
                    json=payload,
                    headers=self.headers
                )
                
                self._handle_api_error(response, operation="update_resume", resume_id=resume_id)
                
                if response.status_code == 200:
                    updated_resume = response.json()
                    logger.info(f"Successfully updated resume {resume_id}")
                    return updated_resume
                else:
                    raise RxResumeAPIError(f"Unexpected status code: {response.status_code}")
                    
        except httpx.TimeoutException as e:
            raise RxResumeNetworkError(
                f"Request timeout while updating resume {resume_id}: {e}",
                error_type="timeout",
                timeout_seconds=self.timeout
            )
        except httpx.ConnectError as e:
            raise RxResumeNetworkError(
                f"Connection error while updating resume {resume_id}: {e}",
                error_type="connection"
            )
        except Exception as e:
            if isinstance(e, (RxResumeAPIError, RxResumeAuthenticationError, 
                            RxResumeValidationError, RxResumeNotFoundError)):
                raise
            raise RxResumeNetworkError(f"Unexpected error during resume update: {e}")
    
    async def delete_resume(self, resume_id: str) -> bool:
        """
        Delete a resume on RxResume.
        
        Args:
            resume_id: The ID of the resume to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            RxResumeAuthenticationError: If API key is invalid
            RxResumeNotFoundError: If resume ID doesn't exist
            RxResumeNetworkError: For network/connection issues
            RxResumeAPIError: For other API errors
        """
        if not self.api_key:
            raise RxResumeAuthenticationError("RxResume API key not configured", api_key_provided=False)
        
        url = f"{self.base_url}/resumes/{resume_id}"
        
        logger.debug(f"Deleting resume {resume_id} on RxResume")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(
                    url,
                    headers=self.headers
                )
                
                self._handle_api_error(response, operation="delete_resume", resume_id=resume_id)
                
                if response.status_code in [200, 204]:
                    logger.info(f"Successfully deleted resume {resume_id}")
                    return True
                else:
                    raise RxResumeAPIError(f"Unexpected status code for deletion: {response.status_code}")
                    
        except httpx.TimeoutException as e:
            raise RxResumeNetworkError(
                f"Request timeout while deleting resume {resume_id}: {e}",
                error_type="timeout",
                timeout_seconds=self.timeout
            )
        except httpx.ConnectError as e:
            raise RxResumeNetworkError(
                f"Connection error while deleting resume {resume_id}: {e}",
                error_type="connection"
            )
        except Exception as e:
            if isinstance(e, (RxResumeAPIError, RxResumeAuthenticationError, RxResumeNotFoundError)):
                raise
            raise RxResumeNetworkError(f"Unexpected error during resume deletion: {e}")
    
    async def get_templates(self) -> List[RxResumeTemplate]:
        """
        Fetch available templates from RxResume.
        
        Returns:
            List[RxResumeTemplate]: List of available templates
            
        Raises:
            RxResumeAuthenticationError: If API key is invalid
            RxResumeNetworkError: For network/connection issues
            RxResumeAPIError: For other API errors
        """
        if not self.api_key:
            raise RxResumeAuthenticationError("RxResume API key not configured", api_key_provided=False)
        
        url = f"{self.base_url}/templates"
        
        logger.debug("Fetching available templates from RxResume")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers=self.headers
                )
                
                self._handle_api_error(response, operation="get_templates")
                
                if response.status_code == 200:
                    templates_data = response.json()
                    # Note: Actual endpoint structure may vary, adjust as needed
                    templates = []
                    if isinstance(templates_data, list):
                        for template_data in templates_data:
                            try:
                                template = RxResumeTemplate(**template_data)
                                templates.append(template)
                            except Exception as e:
                                logger.warning(f"Failed to parse template: {e}")
                    
                    logger.info(f"Successfully fetched {len(templates)} templates")
                    return templates
                else:
                    raise RxResumeAPIError(f"Unexpected status code: {response.status_code}")
                    
        except httpx.TimeoutException as e:
            raise RxResumeNetworkError(
                f"Request timeout while fetching templates: {e}",
                error_type="timeout",
                timeout_seconds=self.timeout
            )
        except httpx.ConnectError as e:
            raise RxResumeNetworkError(
                f"Connection error while fetching templates: {e}",
                error_type="connection"
            )
        except Exception as e:
            if isinstance(e, (RxResumeAPIError, RxResumeAuthenticationError)):
                raise
            raise RxResumeNetworkError(f"Unexpected error during template fetch: {e}")
    
    def _handle_api_error(self, response: httpx.Response, operation: str = "unknown", resume_id: Optional[str] = None) -> None:
        """
        Handle API error responses and raise appropriate exceptions.
        
        Args:
            response: HTTP response object
            operation: The operation being performed
            resume_id: Optional resume ID for context
        """
        if response.status_code == 200:
            return  
        
        try:
            error_data = response.json()
        except Exception:
            error_data = {"message": response.text or "Unknown error"}
        
        if response.status_code == 401:
            raise RxResumeAuthenticationError(
                f"Authentication failed for {operation}: {error_data.get('message', 'Invalid API key')}",
                api_key_provided=bool(self.api_key)
            )
        
        elif response.status_code == 404:
            message = error_data.get('message', f'Resume {resume_id} not found')
            raise RxResumeNotFoundError(message, resume_id=resume_id)
        
        elif response.status_code == 400:
            # Check for specific validation errors
            if error_data.get('code') == 'RESUME_SLUG_ALREADY_EXISTS':
                raise RxResumeSlugExistsError(
                    error_data.get('message', 'Resume slug already exists'),
                    slug=error_data.get('slug')
                )
            else:
                validation_data = error_data.get('data', {})
                validation_errors = None
                if isinstance(validation_data, dict):
                    validation_errors = validation_data
                raise RxResumeValidationError(
                    f"Validation error in {operation}: {error_data.get('message', 'Invalid data')}",
                    validation_errors=validation_errors
                )
        
        else:
            raise RxResumeAPIError(
                f"API error in {operation}: {error_data.get('message', 'Unknown error')}",
                status_code=response.status_code,
                response_data=error_data
            )
