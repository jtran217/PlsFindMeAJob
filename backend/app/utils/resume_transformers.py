"""
Data transformation utilities for Resume <-> RxResume format conversion.
Handles bidirectional transformation between local resume format and RxResume API format.
"""
import logging
from typing import Dict, Any, Optional, List
import re
import uuid
from datetime import datetime

from app.models.resume_schemas import Resume, EnhancedBasics, ResumeData
from app.core.config import settings

logger = logging.getLogger(__name__)


class ResumeTransformer:
    """
    Utility class for transforming between local Resume and RxResume formats.
    
    Handles data transformation, template mapping, and format conversion
    for seamless integration with RxResume API.
    """
    
    # Template mapping based on design preferences
    TEMPLATE_MAPPINGS = {
        # Professional/minimal templates
        "#000000": "azurill",  # Black - professional
        "#333333": "azurill",  # Dark gray - professional
        "#ffffff": "azurill",  # White - minimal
        
        # Modern/tech templates
        "#0066cc": "onyx",     # Blue - tech
        "#1a73e8": "onyx",     # Google blue - modern
        "#0052cc": "onyx",     # Dark blue - corporate
        
        # Creative templates
        "#ff6b6b": "bronzor",  # Red - creative
        "#4ecdc4": "bronzor",  # Teal - creative
        "#45b7d1": "bronzor",  # Light blue - creative
        "#96ceb4": "bronzor",  # Green - creative
    }
    
    @staticmethod
    def local_to_rxresume(local_resume: Resume) -> Dict[str, Any]:
        """
        Convert local Resume to RxResume ResumeData format.
        
        Args:
            local_resume: Local Resume object
            
        Returns:
            Dict[str, Any]: Resume data in RxResume format
        """
        logger.debug("Converting local resume to RxResume format")
        
        try:
            # Transform basic information
            basics = ResumeTransformer._transform_basics(local_resume.data.basics)
            
            # Transform sections
            sections = ResumeTransformer._transform_sections(local_resume.data.sections)
            
            # Transform metadata and design
            metadata = ResumeTransformer._transform_metadata(local_resume.data.metadata)
            
            # Create RxResume data structure
            rxresume_data = {
                "picture": ResumeTransformer._transform_picture(local_resume.data.picture),
                "basics": basics,
                "summary": ResumeTransformer._transform_summary(local_resume.data.summary),
                "sections": sections,
                "metadata": metadata
            }
            
            logger.debug("Successfully converted local resume to RxResume format")
            return rxresume_data
            
        except Exception as e:
            logger.error(f"Failed to transform local resume to RxResume format: {e}")
            raise ValueError(f"Resume transformation failed: {e}")
    
    @staticmethod
    def _transform_basics(enhanced_basics: EnhancedBasics) -> Dict[str, Any]:
        """Transform enhanced basics to RxResume basics format."""
        return {
            "name": enhanced_basics.name or "",
            "headline": enhanced_basics.headline or "",
            "email": enhanced_basics.email or "",
            "phone": enhanced_basics.phone or "",
            "location": enhanced_basics.location or "",
            "website": {
                "url": enhanced_basics.website.url or "",
                "label": enhanced_basics.website.label or ""
            },
            "customFields": [
                {
                    "id": field.id,
                    "icon": field.icon or "",
                    "text": field.text or "",
                    "link": field.link or ""
                }
                for field in enhanced_basics.customFields
            ]
        }
    
    @staticmethod
    def _transform_picture(picture) -> Dict[str, Any]:
        """Transform picture settings to RxResume format."""
        return {
            "hidden": picture.hidden,
            "url": picture.url or "",
            "size": picture.size,
            "rotation": picture.rotation,
            "aspectRatio": picture.aspectRatio,
            "borderRadius": picture.borderRadius,
            "borderColor": picture.borderColor or "",
            "borderWidth": picture.borderWidth,
            "shadowColor": picture.shadowColor or "",
            "shadowWidth": picture.shadowWidth
        }
    
    @staticmethod
    def _transform_summary(summary) -> Dict[str, Any]:
        """Transform summary section to RxResume format."""
        return {
            "title": summary.title or "Summary",
            "columns": summary.columns,
            "hidden": summary.hidden,
            "content": summary.content or ""
        }
    
    @staticmethod
    def _transform_sections(sections) -> Dict[str, Any]:
        """Transform all sections to RxResume format."""
        transformed_sections = {}
        
        # Experience section
        transformed_sections["experience"] = {
            "title": sections.experience.title or "Experience",
            "columns": sections.experience.columns,
            "hidden": sections.experience.hidden,
            "items": [
                ResumeTransformer._transform_experience_item(item)
                for item in sections.experience.items
            ]
        }
        
        # Education section
        transformed_sections["education"] = {
            "title": sections.education.title or "Education",
            "columns": sections.education.columns,
            "hidden": sections.education.hidden,
            "items": [
                ResumeTransformer._transform_education_item(item)
                for item in sections.education.items
            ]
        }
        
        # Skills section
        transformed_sections["skills"] = {
            "title": sections.skills.title or "Skills",
            "columns": sections.skills.columns,
            "hidden": sections.skills.hidden,
            "items": [
                ResumeTransformer._transform_skill_item(item)
                for item in sections.skills.items
            ]
        }
        
        # Projects section
        transformed_sections["projects"] = {
            "title": sections.projects.title or "Projects",
            "columns": sections.projects.columns,
            "hidden": sections.projects.hidden,
            "items": [
                ResumeTransformer._transform_project_item(item)
                for item in sections.projects.items
            ]
        }
        
        # Languages section
        transformed_sections["languages"] = {
            "title": sections.languages.title or "Languages",
            "columns": sections.languages.columns,
            "hidden": sections.languages.hidden,
            "items": [
                ResumeTransformer._transform_language_item(item)
                for item in sections.languages.items
            ]
        }
        
        # Profiles section
        transformed_sections["profiles"] = {
            "title": sections.profiles.title or "Profiles",
            "columns": sections.profiles.columns,
            "hidden": sections.profiles.hidden,
            "items": [
                ResumeTransformer._transform_profile_item(item)
                for item in sections.profiles.items
            ]
        }
        
        # Interests section
        transformed_sections["interests"] = {
            "title": sections.interests.title or "Interests",
            "columns": sections.interests.columns,
            "hidden": sections.interests.hidden,
            "items": [
                ResumeTransformer._transform_interest_item(item)
                for item in sections.interests.items
            ]
        }
        
        # Awards section
        transformed_sections["awards"] = {
            "title": sections.awards.title or "Awards",
            "columns": sections.awards.columns,
            "hidden": sections.awards.hidden,
            "items": [
                ResumeTransformer._transform_award_item(item)
                for item in sections.awards.items
            ]
        }
        
        # Certifications section
        transformed_sections["certifications"] = {
            "title": sections.certifications.title or "Certifications",
            "columns": sections.certifications.columns,
            "hidden": sections.certifications.hidden,
            "items": [
                ResumeTransformer._transform_certification_item(item)
                for item in sections.certifications.items
            ]
        }
        
        # Publications section
        transformed_sections["publications"] = {
            "title": sections.publications.title or "Publications",
            "columns": sections.publications.columns,
            "hidden": sections.publications.hidden,
            "items": [
                ResumeTransformer._transform_publication_item(item)
                for item in sections.publications.items
            ]
        }
        
        # Volunteer section
        transformed_sections["volunteer"] = {
            "title": sections.volunteer.title or "Volunteer",
            "columns": sections.volunteer.columns,
            "hidden": sections.volunteer.hidden,
            "items": [
                ResumeTransformer._transform_volunteer_item(item)
                for item in sections.volunteer.items
            ]
        }
        
        # References section
        transformed_sections["references"] = {
            "title": sections.references.title or "References",
            "columns": sections.references.columns,
            "hidden": sections.references.hidden,
            "items": [
                ResumeTransformer._transform_reference_item(item)
                for item in sections.references.items
            ]
        }
        
        return transformed_sections
    
    @staticmethod
    def _transform_experience_item(item) -> Dict[str, Any]:
        """Transform experience item to RxResume format."""
        return {
            "id": item.id,
            "hidden": item.hidden,
            "options": {"showLinkInTitle": item.options.showLinkInTitle},
            "company": item.company or "",
            "position": item.position or "",
            "location": item.location or "",
            "period": item.period or "",
            "website": {
                "url": item.website.url or "",
                "label": item.website.label or ""
            },
            "description": item.description or ""
        }
    
    @staticmethod
    def _transform_education_item(item) -> Dict[str, Any]:
        """Transform education item to RxResume format."""
        return {
            "id": item.id,
            "hidden": item.hidden,
            "options": {"showLinkInTitle": item.options.showLinkInTitle},
            "school": item.school or "",
            "degree": item.degree or "",
            "area": item.area or "",
            "grade": item.grade or "",
            "location": item.location or "",
            "period": item.period or "",
            "website": {
                "url": item.website.url or "",
                "label": item.website.label or ""
            },
            "description": item.description or ""
        }
    
    @staticmethod
    def _transform_skill_item(item) -> Dict[str, Any]:
        """Transform skill item to RxResume format."""
        return {
            "id": item.id,
            "hidden": item.hidden,
            "options": {"showLinkInTitle": item.options.showLinkInTitle},
            "icon": item.icon or "",
            "name": item.name or "",
            "proficiency": item.proficiency or "",
            "level": float(item.level),
            "keywords": item.keywords or []
        }
    
    @staticmethod
    def _transform_project_item(item) -> Dict[str, Any]:
        """Transform project item to RxResume format."""
        return {
            "id": item.id,
            "hidden": item.hidden,
            "options": {"showLinkInTitle": item.options.showLinkInTitle},
            "name": item.name or "",
            "period": item.period or "",
            "website": {
                "url": item.website.url or "",
                "label": item.website.label or ""
            },
            "description": item.description or ""
        }
    
    @staticmethod
    def _transform_language_item(item) -> Dict[str, Any]:
        """Transform language item to RxResume format."""
        return {
            "id": item.id,
            "hidden": item.hidden,
            "options": {"showLinkInTitle": item.options.showLinkInTitle},
            "language": item.language or "",
            "fluency": item.fluency or "",
            "level": float(item.level)
        }
    
    @staticmethod
    def _transform_profile_item(item) -> Dict[str, Any]:
        """Transform profile item to RxResume format."""
        return {
            "id": item.id,
            "hidden": item.hidden,
            "options": {"showLinkInTitle": item.options.showLinkInTitle},
            "icon": item.icon or "",
            "network": item.network or "",
            "username": item.username or "",
            "website": {
                "url": item.website.url or "",
                "label": item.website.label or ""
            }
        }
    
    @staticmethod
    def _transform_interest_item(item) -> Dict[str, Any]:
        """Transform interest item to RxResume format."""
        return {
            "id": item.id,
            "hidden": item.hidden,
            "options": {"showLinkInTitle": item.options.showLinkInTitle},
            "icon": item.icon or "",
            "name": item.name or "",
            "keywords": item.keywords or []
        }
    
    @staticmethod
    def _transform_award_item(item) -> Dict[str, Any]:
        """Transform award item to RxResume format."""
        return {
            "id": item.id,
            "hidden": item.hidden,
            "options": {"showLinkInTitle": item.options.showLinkInTitle},
            "title": item.title or "",
            "awarder": item.awarder or "",
            "date": item.date or "",
            "website": {
                "url": item.website.url or "",
                "label": item.website.label or ""
            },
            "description": item.description or ""
        }
    
    @staticmethod
    def _transform_certification_item(item) -> Dict[str, Any]:
        """Transform certification item to RxResume format."""
        return {
            "id": item.id,
            "hidden": item.hidden,
            "options": {"showLinkInTitle": item.options.showLinkInTitle},
            "title": item.title or "",
            "issuer": item.issuer or "",
            "date": item.date or "",
            "website": {
                "url": item.website.url or "",
                "label": item.website.label or ""
            },
            "description": item.description or ""
        }
    
    @staticmethod
    def _transform_publication_item(item) -> Dict[str, Any]:
        """Transform publication item to RxResume format."""
        return {
            "id": item.id,
            "hidden": item.hidden,
            "options": {"showLinkInTitle": item.options.showLinkInTitle},
            "title": item.title or "",
            "publisher": item.publisher or "",
            "date": item.date or "",
            "website": {
                "url": item.website.url or "",
                "label": item.website.label or ""
            },
            "description": item.description or ""
        }
    
    @staticmethod
    def _transform_volunteer_item(item) -> Dict[str, Any]:
        """Transform volunteer item to RxResume format."""
        return {
            "id": item.id,
            "hidden": item.hidden,
            "options": {"showLinkInTitle": item.options.showLinkInTitle},
            "organization": item.organization or "",
            "location": item.location or "",
            "period": item.period or "",
            "website": {
                "url": item.website.url or "",
                "label": item.website.label or ""
            },
            "description": item.description or ""
        }
    
    @staticmethod
    def _transform_reference_item(item) -> Dict[str, Any]:
        """Transform reference item to RxResume format."""
        return {
            "id": item.id,
            "hidden": item.hidden,
            "options": {"showLinkInTitle": item.options.showLinkInTitle},
            "name": item.name or "",
            "position": item.position or "",
            "website": {
                "url": item.website.url or "",
                "label": item.website.label or ""
            },
            "phone": item.phone or "",
            "description": item.description or ""
        }
    
    @staticmethod
    def _transform_metadata(metadata) -> Dict[str, Any]:
        """Transform metadata to RxResume format."""
        return {
            "template": metadata.template or "azurill",
            "layout": {
                "sidebarWidth": metadata.layout.sidebarWidth,
                "pages": [
                    {
                        "fullWidth": page.fullWidth,
                        "main": page.main,
                        "sidebar": page.sidebar
                    }
                    for page in metadata.layout.pages
                ]
            },
            "css": {
                "enabled": metadata.css.enabled,
                "value": metadata.css.value or ""
            },
            "page": {
                "gapX": metadata.page.gapX,
                "gapY": metadata.page.gapY,
                "marginX": metadata.page.marginX,
                "marginY": metadata.page.marginY,
                "format": metadata.page.format,
                "locale": metadata.page.locale,
                "hideIcons": metadata.page.hideIcons
            },
            "design": {
                "level": {
                    "icon": metadata.design.level.icon or "",
                    "type": metadata.design.level.type
                },
                "colors": {
                    "primary": metadata.design.colors.primary,
                    "text": metadata.design.colors.text,
                    "background": metadata.design.colors.background
                }
            },
            "typography": {
                "body": {
                    "fontFamily": metadata.typography.body.fontFamily or "",
                    "fontWeights": metadata.typography.body.fontWeights,
                    "fontSize": metadata.typography.body.fontSize,
                    "lineHeight": metadata.typography.body.lineHeight
                },
                "heading": {
                    "fontFamily": metadata.typography.heading.fontFamily or "",
                    "fontWeights": metadata.typography.heading.fontWeights,
                    "fontSize": metadata.typography.heading.fontSize,
                    "lineHeight": metadata.typography.heading.lineHeight
                }
            },
            "notes": metadata.notes or ""
        }
    
    @staticmethod
    def map_template(local_resume: Resume, user_override: Optional[str] = None) -> str:
        """
        Map local design preferences to RxResume template.
        
        Args:
            local_resume: Local Resume object
            user_override: Manual template selection override
            
        Returns:
            str: RxResume template identifier
        """
        if user_override:
            logger.debug(f"Using user-specified template override: {user_override}")
            return user_override
        
        # Get primary color from design
        try:
            primary_color = local_resume.data.metadata.design.colors.primary.lower()
            
            # Check exact matches first
            if primary_color in ResumeTransformer.TEMPLATE_MAPPINGS:
                template = ResumeTransformer.TEMPLATE_MAPPINGS[primary_color]
                logger.debug(f"Mapped color {primary_color} to template {template}")
                return template
            
            # Check for color categories
            if any(blue in primary_color for blue in ["blue", "0066", "1a73", "0052"]):
                template = "onyx"
            elif primary_color in ["#000000", "#333333", "#ffffff"]:
                template = "azurill"
            elif primary_color != "#000000":  # Any non-black color
                template = "bronzor"
            else:
                template = settings.rxresume_default_template
            
            logger.debug(f"Mapped color {primary_color} to template {template} (category match)")
            return template
            
        except Exception as e:
            logger.warning(f"Failed to map template from design: {e}, using default")
            return settings.rxresume_default_template
    
    @staticmethod
    def generate_resume_name(job_title: str, company: str) -> str:
        """
        Generate human-readable resume name for job application.
        
        Args:
            job_title: Position title
            company: Company name
            
        Returns:
            str: Formatted resume name like "Resume - Software Engineer at Google"
        """
        # Clean up the inputs
        clean_title = re.sub(r'[^\w\s-]', '', job_title).strip()
        clean_company = re.sub(r'[^\w\s-]', '', company).strip()
        
        # Truncate if too long (RxResume has 64 char limit)
        if len(clean_title) > 25:
            clean_title = clean_title[:25].strip()
        if len(clean_company) > 25:
            clean_company = clean_company[:25].strip()
        
        resume_name = f"Resume - {clean_title} at {clean_company}"
        
        # Ensure it doesn't exceed RxResume's 64 character limit
        if len(resume_name) > 64:
            # Fallback to shorter format
            resume_name = f"Resume - {clean_company}"
            if len(resume_name) > 64:
                resume_name = f"Resume - {clean_company[:50]}"
        
        logger.debug(f"Generated resume name: {resume_name}")
        return resume_name
    
    @staticmethod
    def generate_unique_slug(base_name: str, existing_slugs: Optional[List[str]] = None) -> str:
        """
        Generate URL-friendly slug from resume name.
        
        Args:
            base_name: Base name to convert to slug
            existing_slugs: List of existing slugs to avoid conflicts
            
        Returns:
            str: Unique URL-friendly slug
        """
        existing_slugs = existing_slugs or []
        
        # Convert to slug format
        slug = re.sub(r'[^\w\s-]', '', base_name.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        
        # Ensure it's not empty
        if not slug:
            slug = "resume"
        
        # Ensure uniqueness
        original_slug = slug
        counter = 1
        while slug in existing_slugs:
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        # Ensure it doesn't exceed RxResume's 64 character limit
        if len(slug) > 64:
            slug = slug[:60]  # Leave room for potential suffix
            
        logger.debug(f"Generated unique slug: {slug}")
        return slug