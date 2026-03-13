"""
Resume data models for the optimization system.

This module contains Pydantic models for representing resume data,
including automatic keyword extraction and job analysis structures.
"""

from __future__ import annotations
from typing import List, Dict, TYPE_CHECKING
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

if TYPE_CHECKING:
    from app.services.keyword_extraction import KeywordExtractor


def _get_keyword_extractor() -> KeywordExtractor:
    """
    Lazy import of KeywordExtractor to avoid circular imports.
    
    Returns:
        KeywordExtractor instance
    """
    from app.services.keyword_extraction import KeywordExtractor
    return KeywordExtractor()


class PersonalInfo(BaseModel):
    """Personal contact information section of a resume."""
    name: str = ""
    phone: str = ""
    email: str = ""
    linkedin: str = ""
    github: str = ""


class Education(BaseModel):
    """Educational background entry."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    institution: str = ""
    location: str = ""
    degree: str = ""
    duration: str = ""


class TechnicalSkills(BaseModel):
    """Technical skills organized by category."""
    languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    developer_tools: List[str] = Field(default_factory=list)
    libraries: List[str] = Field(default_factory=list)


class BulletPoint(BaseModel):
    """
    Individual bullet point with automatic keyword extraction.
    
    Keywords and category are automatically extracted from the text
    when the bullet point is created or when text is updated.
    """
    model_config = ConfigDict(validate_assignment=True)

    id: str = Field(default_factory=lambda: str(uuid4()))
    text: str
    keywords: List[str] = Field(default_factory=list)
    category: str = "technical"
    
    @model_validator(mode='after')
    def extract_keywords_if_missing(self) -> BulletPoint:
        """Extract keywords and categorize if not provided."""
        if self.text and not self.keywords:
            extractor = _get_keyword_extractor()
            self.keywords = extractor.extract_keywords(self.text)
            self.category = extractor.categorize_content(self.text, self.keywords)
        return self


class Experience(BaseModel):
    """Work experience with associated bullet points."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = ""
    company: str = ""
    location: str = ""
    duration: str = ""
    bullet_points: List[BulletPoint] = Field(default_factory=list)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    @property
    def overall_keywords(self) -> List[str]:
        """Aggregate keywords from all bullet points, deduplicated and sorted.
        
        Kept as a plain property (not @computed_field) to prevent Pydantic from
        serializing it into JSON. Serializing a computed field causes a
        ValidationError on reload because computed fields cannot be set from
        input data.
        """
        all_keywords = []
        for bullet in self.bullet_points:
            all_keywords.extend(bullet.keywords)
        return sorted(list(set(all_keywords)))


class Project(BaseModel):
    """Personal or professional project with associated bullet points."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = ""
    technologies: str = ""
    duration: str = ""
    bullet_points: List[BulletPoint] = Field(default_factory=list)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    @property
    def overall_keywords(self) -> List[str]:
        """Aggregate keywords from all bullet points, deduplicated and sorted.
        
        Kept as a plain property (not @computed_field) to prevent Pydantic from
        serializing it into JSON. Serializing a computed field causes a
        ValidationError on reload because computed fields cannot be set from
        input data.
        """
        all_keywords = []
        for bullet in self.bullet_points:
            all_keywords.extend(bullet.keywords)
        return sorted(list(set(all_keywords)))


class Resume(BaseModel):
    """Complete resume data structure containing all sections."""
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    education: List[Education] = Field(default_factory=list)
    technical_skills: TechnicalSkills = Field(default_factory=TechnicalSkills)
    experiences: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)


# Future optimization models for AI enhancement phases
class OptimizedBullet(BaseModel):
    """Optimized bullet point with original and AI-enhanced versions."""
    bullet_id: str
    original: str
    optimized: str


class OptimizedExperienceContent(BaseModel):
    """AI-optimized content for a specific experience."""
    optimized_bullet_points: List[OptimizedBullet] = Field(default_factory=list)


class OptimizedProjectContent(BaseModel):
    """AI-optimized content for a specific project."""
    optimized_bullet_points: List[OptimizedBullet] = Field(default_factory=list)


class OptimizedContent(BaseModel):
    """Container for all AI-optimized content organized by item ID."""
    experiences: Dict[str, OptimizedExperienceContent] = Field(default_factory=dict)
    projects: Dict[str, OptimizedProjectContent] = Field(default_factory=dict)


class OptimizedResume(BaseModel):
    """Job-specific optimized resume version with AI enhancements."""
    job_id: str
    generated_at: str
    selected_experiences: List[str] = Field(default_factory=list)
    selected_projects: List[str] = Field(default_factory=list)
    optimized_content: OptimizedContent = Field(default_factory=OptimizedContent)


# API Response models
class JobAnalysis(BaseModel):
    """Result of analyzing job requirements for resume optimization."""
    job_id: str
    keywords: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    job_title: str = ""
    company: str = ""
    job_description: str = ""


class JobAnalysisResult(BaseModel):
    """Complete job analysis with ranked experiences and projects."""
    job_analysis: JobAnalysis
    ranked_experiences: List[Experience] = Field(default_factory=list)
    ranked_projects: List[Project] = Field(default_factory=list)