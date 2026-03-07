"""
Profile migration utility to convert between old and new resume formats.
Handles transformation of legacy profile data to the enhanced resume schema.
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.models.schemas import Profile as LegacyProfile
from app.models.resume_schemas import (
    Resume, ResumeData, EnhancedBasics, Website, 
    ExperienceSection, ExperienceItem, EducationSection, EducationItem,
    ProjectsSection, ProjectItem, SkillsSection, SkillItem,
    ProfilesSection, ProfileItem, Summary, ResumeSections
)

logger = logging.getLogger(__name__)


class ProfileMigrator:
    """Handles migration between old and new profile formats."""
    
    def __init__(self):
        """Initialize the migrator."""
        self.logger = logging.getLogger(__name__)
    
    def migrate_legacy_to_resume(self, legacy_data: Dict[str, Any]) -> Resume:
        """
        Convert legacy profile format to new resume format.
        
        Args:
            legacy_data: Dictionary containing legacy profile data
            
        Returns:
            Resume: New resume format instance
        """
        try:
            # First validate the legacy data
            legacy_profile = LegacyProfile(**legacy_data)
            
            # Extract basic information
            basics = self._migrate_basics(legacy_profile.basics)
            
            sections = ResumeSections(
                experience=self._migrate_experience(legacy_profile.experiences),
                education=self._migrate_education(legacy_profile.education),
                projects=self._migrate_projects(legacy_profile.projects),
                skills=self._migrate_skills(legacy_profile.skills),
                profiles=self._migrate_profiles(legacy_profile.basics)
            )
            
            resume_data = ResumeData(
                basics=basics,
                summary=Summary(content=""),
                sections=sections
            )
            
            resume_name = basics.name or "My Resume"
            
            resume = Resume(
                name=resume_name,
                slug="",
                tags=self._generate_tags(legacy_profile),
                data=resume_data,
                isPublic=True
            )
            
            self.logger.info(f"Successfully migrated profile for {basics.name}")
            return resume
            
        except Exception as e:
            self.logger.error(f"Failed to migrate profile: {e}")
            raise ValueError(f"Migration failed: {e}")
    
    def _migrate_basics(self, legacy_basics: Any) -> EnhancedBasics:
        """Convert legacy basics to enhanced basics format."""
        website = Website()
        
        if hasattr(legacy_basics, 'linkedin') and legacy_basics.linkedin:
            website = Website(
                url=legacy_basics.linkedin,
                label="LinkedIn Profile"
            )
        
        return EnhancedBasics(
            name=legacy_basics.name,
            headline="",
            email=legacy_basics.email,
            phone=getattr(legacy_basics, 'phone', ''),
            location="",
            website=website,
            customFields=[]
        )
    
    def _migrate_experience(self, legacy_experiences: List[Any]) -> ExperienceSection:
        """Convert legacy experiences to new experience section."""
        items = []
        
        for i, exp in enumerate(legacy_experiences):
            description = ""
            if hasattr(exp, 'bullets') and exp.bullets:
                description = "• " + "\n• ".join(exp.bullets)
            
            period = ""
            if hasattr(exp, 'start_date') and hasattr(exp, 'end_date'):
                start = exp.start_date or ""
                end = exp.end_date or "Present"
                if start or end != "Present":
                    period = f"{start} - {end}" if start else end
            
            item = ExperienceItem(
                id=f"experience-{i+1}",
                company=getattr(exp, 'company', ''),
                position=getattr(exp, 'position', ''),
                location=getattr(exp, 'location', ''),
                period=period,
                description=description,
                website=Website(),
                hidden=False
            )
            items.append(item)
        
        return ExperienceSection(items=items)
    
    def _migrate_education(self, legacy_education: List[Any]) -> EducationSection:
        """Convert legacy education to new education section."""
        items = []
        
        for i, edu in enumerate(legacy_education):
            period = ""
            if hasattr(edu, 'start_date') and hasattr(edu, 'expected_date'):
                start = edu.start_date or ""
                expected = edu.expected_date or ""
                if start or expected:
                    period = f"{start} - {expected}" if start else expected
            
            item = EducationItem(
                id=f"education-{i+1}",
                school=getattr(edu, 'institution', ''),
                degree=getattr(edu, 'degree', ''),
                area=getattr(edu, 'degree', ''),  # Use degree as area for now
                location=getattr(edu, 'location', ''),
                period=period,
                description=getattr(edu, 'coursework', ''),
                website=Website(),
                hidden=False
            )
            items.append(item)
        
        return EducationSection(items=items)
    
    def _migrate_projects(self, legacy_projects: List[Any]) -> ProjectsSection:
        """Convert legacy projects to new projects section."""
        items = []
        
        for i, proj in enumerate(legacy_projects):
            item = ProjectItem(
                id=f"project-{i+1}",
                name=getattr(proj, 'name', ''),
                description=getattr(proj, 'description', ''),
                period="",  # User will need to add this
                website=Website(),
                hidden=False
            )
            items.append(item)
        
        return ProjectsSection(items=items)
    
    def _migrate_skills(self, legacy_skills: List[str]) -> SkillsSection:
        """Convert legacy skills array to new skills section."""
        items = []
        
        for i, skill in enumerate(legacy_skills):
            item = SkillItem(
                id=f"skill-{i+1}",
                name=skill,
                proficiency="Intermediate",  # Default proficiency
                level=3.0,  # Default level (out of 5)
                keywords=[skill],  # Use skill name as keyword
                hidden=False
            )
            items.append(item)
        
        return SkillsSection(items=items)
    
    def _migrate_profiles(self, legacy_basics: Any) -> ProfilesSection:
        """Create profiles section from legacy basic info."""
        items = []
        
        # Add GitHub profile if present
        if hasattr(legacy_basics, 'github') and legacy_basics.github:
            github_item = ProfileItem(
                id="profile-github",
                icon="github",
                network="GitHub",
                username="",  # Extract from URL if needed
                website=Website(
                    url=legacy_basics.github,
                    label="GitHub Profile"
                ),
                hidden=False
            )
            items.append(github_item)
        
        return ProfilesSection(items=items)
    
    def _generate_tags(self, legacy_profile: Any) -> List[str]:
        """Generate appropriate tags based on legacy profile content."""
        tags = []
        
        # Add tags based on skills
        if hasattr(legacy_profile, 'skills'):
            # Add technology-related tags
            tech_skills = [skill.lower() for skill in legacy_profile.skills]
            if any(skill in tech_skills for skill in ['python', 'javascript', 'react', 'node']):
                tags.append("Software Development")
            if any(skill in tech_skills for skill in ['aws', 'azure', 'cloud', 'docker']):
                tags.append("Cloud Computing")
            if any(skill in tech_skills for skill in ['sql', 'database', 'mongodb']):
                tags.append("Database")
        
        # Add default tag if none found
        if not tags:
            tags.append("Technology")
        
        return tags
    
    def migrate_resume_to_legacy(self, resume: Resume) -> Dict[str, Any]:
        """
        Convert new resume format back to legacy profile format.
        Used for backward compatibility.
        
        Args:
            resume: Resume instance to convert
            
        Returns:
            Dict containing legacy profile data
        """
        try:
            # Extract basics
            basics_data = {
                "name": resume.data.basics.name,
                "email": resume.data.basics.email,
                "phone": resume.data.basics.phone,
                "linkedin": resume.data.basics.website.url if resume.data.basics.website.url else "",
                "github": ""
            }
            
            # Find GitHub in profiles
            for profile in resume.data.sections.profiles.items:
                if profile.network.lower() == "github":
                    basics_data["github"] = profile.website.url
                    break
            
            # Convert experiences
            experiences = []
            for exp in resume.data.sections.experience.items:
                # Convert description back to bullets
                bullets = []
                if exp.description:
                    # Simple conversion - split on bullet points
                    lines = exp.description.split('\n')
                    bullets = [line.replace('•', '').strip() for line in lines if line.strip()]
                
                # Parse period back to dates
                start_date = ""
                end_date = ""
                if exp.period:
                    parts = exp.period.split(' - ')
                    if len(parts) == 2:
                        start_date = parts[0]
                        end_date = parts[1] if parts[1] != "Present" else ""
                
                exp_data = {
                    "company": exp.company,
                    "position": exp.position,
                    "start_date": start_date,
                    "end_date": end_date,
                    "location": exp.location,
                    "bullets": bullets
                }
                experiences.append(exp_data)
            
            # Convert education
            education = []
            for edu in resume.data.sections.education.items:
                # Parse period back to dates
                start_date = ""
                expected_date = ""
                if edu.period:
                    parts = edu.period.split(' - ')
                    if len(parts) == 2:
                        start_date = parts[0]
                        expected_date = parts[1]
                
                edu_data = {
                    "institution": edu.school,
                    "location": edu.location,
                    "degree": edu.degree,
                    "expected_date": expected_date,
                    "start_date": start_date,
                    "coursework": edu.description
                }
                education.append(edu_data)
            
            # Convert skills
            skills = [skill.name for skill in resume.data.sections.skills.items]
            
            # Convert projects
            projects = []
            for proj in resume.data.sections.projects.items:
                proj_data = {
                    "name": proj.name,
                    "description": proj.description
                }
                projects.append(proj_data)
            
            legacy_data = {
                "basics": basics_data,
                "experiences": experiences,
                "education": education,
                "skills": skills,
                "projects": projects
            }
            
            self.logger.info("Successfully converted resume to legacy format")
            return legacy_data
            
        except Exception as e:
            self.logger.error(f"Failed to convert resume to legacy: {e}")
            raise ValueError(f"Legacy conversion failed: {e}")
    
    def detect_format(self, data: Dict[str, Any]) -> str:
        """
        Detect whether the data is in legacy or new resume format.
        
        Args:
            data: Profile/resume data dictionary
            
        Returns:
            str: "legacy" or "resume"
        """
        # Check for new resume format indicators
        if "data" in data and "name" in data and "slug" in data:
            return "resume"
        
        # Check for legacy format indicators
        if "basics" in data and "experiences" in data:
            return "legacy"
        
        # Default to legacy for safety
        return "legacy"