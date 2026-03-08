"""
RxResume API request and response schemas.
Defines Pydantic models for RxResume API integration.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import re


# RxResume API Request Schemas

class RxResumeCreateRequest(BaseModel):
    """Request schema for creating a new resume on RxResume."""
    name: str = Field(..., min_length=1, max_length=64, description="The name of the resume")
    slug: str = Field(..., min_length=1, max_length=64, description="The slug of the resume")
    tags: List[str] = Field(default=[], description="The tags of the resume")
    withSampleData: bool = Field(default=False, description="Initialize with sample data")
    
    @validator('slug')
    def validate_slug(cls, v):
        """Ensure slug is URL-friendly."""
        if not re.match(r'^[a-z0-9-_]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, hyphens, and underscores')
        return v


class RxResumeUpdateRequest(BaseModel):
    """Request schema for updating an existing resume on RxResume."""
    name: Optional[str] = Field(None, min_length=1, max_length=64, description="The name of the resume")
    slug: Optional[str] = Field(None, min_length=1, max_length=64, description="The slug of the resume")
    tags: Optional[List[str]] = Field(None, description="The tags of the resume")
    data: Optional[Dict[str, Any]] = Field(None, description="The resume data in RxResume format")
    isPublic: Optional[bool] = Field(None, description="Whether the resume is public")
    
    @validator('slug')
    def validate_slug(cls, v):
        """Ensure slug is URL-friendly."""
        if v is not None and not re.match(r'^[a-z0-9-_]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, hyphens, and underscores')
        return v

# RxResume API Response Schemas

class RxResumeCreateResponse(BaseModel):
    """Response schema for resume creation."""
    resume_id: str = Field(..., description="The ID of the newly created resume")


class RxResumeUpdateResponse(BaseModel):
    """Response schema for resume updates - full resume object."""
    id: str = Field(..., description="The ID of the resume")
    name: str = Field(..., description="The name of the resume")
    slug: str = Field(..., description="The slug of the resume")
    tags: List[str] = Field(..., description="The tags of the resume")
    isPublic: bool = Field(..., description="Whether the resume is public")
    isLocked: bool = Field(..., description="Whether the resume is locked")
    data: Dict[str, Any] = Field(..., description="The full resume data")


class RxResumeErrorResponse(BaseModel):
    """Standard error response from RxResume API."""
    defined: bool = Field(..., description="Whether this is a defined error")
    code: str = Field(..., description="Error code")
    status: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
    data: Dict[str, Any] = Field(default={}, description="Additional error data")


class RxResumeTemplate(BaseModel):
    """Schema for RxResume template information."""
    id: str = Field(..., description="Template identifier")
    name: str = Field(..., description="Template display name")
    description: Optional[str] = Field(None, description="Template description")
    category: Optional[str] = Field(None, description="Template category")
    preview_url: Optional[str] = Field(None, description="Template preview image URL")


class RxResumeTemplateListResponse(BaseModel):
    """Response schema for template list endpoint."""
    templates: List[RxResumeTemplate] = Field(..., description="Available templates")


# Internal Schemas for Resume-Job Associations

class ResumeJobCreate(BaseModel):
    """Schema for creating a new resume-job association."""
    job_id: str = Field(..., description="Job posting ID")
    rxresume_id: str = Field(..., description="RxResume resume ID")
    resume_name: str = Field(..., description="Human-readable resume name")
    template: str = Field(default="azurill", description="RxResume template used")
    user_template_override: Optional[str] = Field(None, description="Manual template override")


class ResumeJobResponse(BaseModel):
    """Schema for resume-job association responses."""
    id: int = Field(..., description="Internal database ID")
    job_id: str = Field(..., description="Job posting ID")
    rxresume_id: str = Field(..., description="RxResume resume ID")
    resume_name: str = Field(..., description="Human-readable resume name")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    sync_status: str = Field(..., description="Sync status: synced|pending|failed|error")
    template: str = Field(..., description="RxResume template used")
    user_template_override: Optional[str] = Field(None, description="Manual template override")


class ResumeJobListResponse(BaseModel):
    """Response schema for listing resume-job associations."""
    total: int = Field(..., description="Total number of associations")
    resumes: List[ResumeJobResponse] = Field(..., description="List of resume-job associations")


class BulkSyncRequest(BaseModel):
    """Request schema for bulk syncing resumes."""
    job_ids: Optional[List[str]] = Field(None, description="Specific job IDs to sync (all if None)")
    force_update: bool = Field(default=False, description="Force update even if already synced")
    template_override: Optional[str] = Field(None, description="Override template for all")


class BulkSyncResponse(BaseModel):
    """Response schema for bulk sync operations."""
    total_jobs: int = Field(..., description="Total jobs processed")
    successful: int = Field(..., description="Number of successful syncs")
    failed: int = Field(..., description="Number of failed syncs")
    errors: List[Dict[str, str]] = Field(default=[], description="List of errors")
    created_resumes: List[str] = Field(default=[], description="Newly created resume IDs")
    updated_resumes: List[str] = Field(default=[], description="Updated resume IDs")


# Template Mapping Schemas

class TemplateMapping(BaseModel):
    """Schema for template mapping configuration."""
    color_primary: str = Field(..., description="Primary color to match")
    template_id: str = Field(..., description="Corresponding RxResume template")
    category: str = Field(..., description="Template category")
    description: str = Field(..., description="Mapping description")


class TemplateMappingResponse(BaseModel):
    """Response schema for template mapping."""
    template_id: str = Field(..., description="Selected template ID")
    mapping_reason: str = Field(..., description="Reason for template selection")
    available_templates: List[RxResumeTemplate] = Field(default=[], description="All available templates")
