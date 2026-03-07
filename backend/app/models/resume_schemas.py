"""
Resume optimization schemas based on the enhanced resume format.
These schemas support the comprehensive resume structure with all sections.
"""
from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict, Any, Union
import re
from datetime import datetime


# Common nested types
class Website(BaseModel):
    """Website/URL reference with label."""
    url: str = ""
    label: str = ""


class ItemOptions(BaseModel):
    """Common options for resume items."""
    showLinkInTitle: bool = True


# Picture configuration
class Picture(BaseModel):
    """Profile picture configuration and styling."""
    hidden: bool = True
    url: str = ""
    size: int = 272
    rotation: int = 0
    aspectRatio: float = 1.0
    borderRadius: int = 0
    borderColor: str = ""
    borderWidth: int = 0
    shadowColor: str = ""
    shadowWidth: int = 0


# Enhanced Basics section
class CustomField(BaseModel):
    """Custom contact field."""
    id: str
    icon: str = ""
    text: str = ""
    link: str = ""


class EnhancedBasics(BaseModel):
    """Enhanced basic profile information."""
    name: str
    headline: str = ""
    email: str
    phone: str = ""
    location: str = ""
    website: Website = Website()
    customFields: List[CustomField] = []
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if v and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', v):
            raise ValueError('Please enter a valid email address')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name is not empty."""
        if not v.strip():
            raise ValueError('Name is required')
        return v.strip()


# Summary section
class Summary(BaseModel):
    """Professional summary/objective section."""
    title: str = "Summary"
    columns: int = 1
    hidden: bool = False
    content: str = ""


# Section items for different resume sections
class ProfileItem(BaseModel):
    """Social media/professional profile item."""
    id: str
    hidden: bool = False
    icon: str = ""
    network: str = ""
    username: str = ""
    website: Website = Website()
    options: ItemOptions = ItemOptions()


class ExperienceItem(BaseModel):
    """Work experience item."""
    id: str
    hidden: bool = False
    company: str = ""
    position: str = ""
    location: str = ""
    period: str = ""
    website: Website = Website()
    description: str = ""
    options: ItemOptions = ItemOptions()


class EducationItem(BaseModel):
    """Education item."""
    id: str
    hidden: bool = False
    school: str = ""
    degree: str = ""
    area: str = ""
    grade: str = ""
    location: str = ""
    period: str = ""
    website: Website = Website()
    description: str = ""
    options: ItemOptions = ItemOptions()


class ProjectItem(BaseModel):
    """Project item."""
    id: str
    hidden: bool = False
    name: str = ""
    period: str = ""
    website: Website = Website()
    description: str = ""
    options: ItemOptions = ItemOptions()


class SkillItem(BaseModel):
    """Skill item with proficiency and keywords."""
    id: str
    hidden: bool = False
    icon: str = ""
    name: str = ""
    proficiency: str = ""
    level: float = Field(ge=0, le=5, default=0)
    keywords: List[str] = []
    options: ItemOptions = ItemOptions()


class LanguageItem(BaseModel):
    """Language proficiency item."""
    id: str
    hidden: bool = False
    language: str = ""
    fluency: str = ""
    level: float = Field(ge=0, le=5, default=0)
    options: ItemOptions = ItemOptions()


class InterestItem(BaseModel):
    """Interest/hobby item."""
    id: str
    hidden: bool = False
    icon: str = ""
    name: str = ""
    keywords: List[str] = []
    options: ItemOptions = ItemOptions()


class AwardItem(BaseModel):
    """Award/achievement item."""
    id: str
    hidden: bool = False
    title: str = ""
    awarder: str = ""
    date: str = ""
    website: Website = Website()
    description: str = ""
    options: ItemOptions = ItemOptions()


class CertificationItem(BaseModel):
    """Professional certification item."""
    id: str
    hidden: bool = False
    title: str = ""
    issuer: str = ""
    date: str = ""
    website: Website = Website()
    description: str = ""
    options: ItemOptions = ItemOptions()


class PublicationItem(BaseModel):
    """Publication/article item."""
    id: str
    hidden: bool = False
    title: str = ""
    publisher: str = ""
    date: str = ""
    website: Website = Website()
    description: str = ""
    options: ItemOptions = ItemOptions()


class VolunteerItem(BaseModel):
    """Volunteer experience item."""
    id: str
    hidden: bool = False
    organization: str = ""
    location: str = ""
    period: str = ""
    website: Website = Website()
    description: str = ""
    options: ItemOptions = ItemOptions()


class ReferenceItem(BaseModel):
    """Professional reference item."""
    id: str
    hidden: bool = False
    name: str = ""
    position: str = ""
    website: Website = Website()
    phone: str = ""
    description: str = ""
    options: ItemOptions = ItemOptions()


# Section containers
class Section(BaseModel):
    """Base section with common properties."""
    title: str
    columns: int = 1
    hidden: bool = False


class ProfilesSection(Section):
    """Social profiles section."""
    title: str = "Profiles"
    items: List[ProfileItem] = []


class ExperienceSection(Section):
    """Work experience section."""
    title: str = "Experience"
    items: List[ExperienceItem] = []


class EducationSection(Section):
    """Education section."""
    title: str = "Education"
    items: List[EducationItem] = []


class ProjectsSection(Section):
    """Projects section."""
    title: str = "Projects"
    items: List[ProjectItem] = []


class SkillsSection(Section):
    """Skills section."""
    title: str = "Skills"
    items: List[SkillItem] = []


class LanguagesSection(Section):
    """Languages section."""
    title: str = "Languages"
    items: List[LanguageItem] = []


class InterestsSection(Section):
    """Interests section."""
    title: str = "Interests"
    items: List[InterestItem] = []


class AwardsSection(Section):
    """Awards section."""
    title: str = "Awards"
    items: List[AwardItem] = []


class CertificationsSection(Section):
    """Certifications section."""
    title: str = "Certifications"
    items: List[CertificationItem] = []


class PublicationsSection(Section):
    """Publications section."""
    title: str = "Publications"
    items: List[PublicationItem] = []


class VolunteerSection(Section):
    """Volunteer section."""
    title: str = "Volunteer"
    items: List[VolunteerItem] = []


class ReferencesSection(Section):
    """References section."""
    title: str = "References"
    items: List[ReferenceItem] = []


# All sections container
class ResumeSections(BaseModel):
    """Container for all resume sections."""
    profiles: ProfilesSection = ProfilesSection()
    experience: ExperienceSection = ExperienceSection()
    education: EducationSection = EducationSection()
    projects: ProjectsSection = ProjectsSection()
    skills: SkillsSection = SkillsSection()
    languages: LanguagesSection = LanguagesSection()
    interests: InterestsSection = InterestsSection()
    awards: AwardsSection = AwardsSection()
    certifications: CertificationsSection = CertificationsSection()
    publications: PublicationsSection = PublicationsSection()
    volunteer: VolunteerSection = VolunteerSection()
    references: ReferencesSection = ReferencesSection()


# Custom sections
class CustomSectionItem(BaseModel):
    """Item for custom sections."""
    id: str
    hidden: bool = False
    recipient: str = ""
    content: str = ""
    options: ItemOptions = ItemOptions()


class CustomSection(Section):
    """Flexible custom section."""
    id: str
    type: str = "summary"
    items: List[CustomSectionItem] = []


# Metadata configuration
class PageLayout(BaseModel):
    """Page layout configuration."""
    fullWidth: bool = False
    main: List[str] = []
    sidebar: List[str] = []


class Layout(BaseModel):
    """Resume layout configuration."""
    sidebarWidth: int = 30
    pages: List[PageLayout] = [PageLayout()]


class CSS(BaseModel):
    """Custom CSS configuration."""
    enabled: bool = False
    value: str = ""


class Page(BaseModel):
    """Page formatting settings."""
    gapX: int = 16
    gapY: int = 16
    marginX: int = 16
    marginY: int = 16
    format: str = "a4"
    locale: str = "en"
    hideIcons: bool = False


class LevelConfig(BaseModel):
    """Proficiency level display configuration."""
    icon: str = ""
    type: str = "hidden"


class Colors(BaseModel):
    """Color theme configuration."""
    primary: str = "#000000"
    text: str = "#000000"
    background: str = "#ffffff"


class Design(BaseModel):
    """Design configuration."""
    level: LevelConfig = LevelConfig()
    colors: Colors = Colors()


class Typography(BaseModel):
    """Typography configuration."""
    fontFamily: str = ""
    fontWeights: List[str] = ["400"]
    fontSize: int = 14
    lineHeight: float = 1.5


class TypographySettings(BaseModel):
    """Typography settings for different text types."""
    body: Typography = Typography()
    heading: Typography = Typography(fontWeights=["600"])


class Metadata(BaseModel):
    """Resume metadata and configuration."""
    template: str = "azurill"
    layout: Layout = Layout()
    css: CSS = CSS()
    page: Page = Page()
    design: Design = Design()
    typography: TypographySettings = TypographySettings()
    notes: str = ""


# Main resume data container
class ResumeData(BaseModel):
    """Main resume data container."""
    picture: Picture = Picture()
    basics: EnhancedBasics
    summary: Summary = Summary()
    sections: ResumeSections = ResumeSections()
    customSections: List[CustomSection] = []
    metadata: Metadata = Metadata()


# Complete resume model
class Resume(BaseModel):
    """Complete resume model matching the optimization schema."""
    name: str
    slug: str = ""
    tags: List[str] = []
    data: ResumeData
    isPublic: bool = True
    
    @validator('name')
    def validate_name(cls, v):
        """Ensure name is not empty."""
        if not v.strip():
            raise ValueError('Resume name is required')
        return v.strip()
    
    @validator('slug', pre=True, always=True)
    def generate_slug(cls, v, values):
        """Generate slug from name if not provided."""
        if not v and 'name' in values:
            # Simple slug generation from name
            import re
            slug = re.sub(r'[^\w\s-]', '', values['name']).strip().lower()
            slug = re.sub(r'[-\s]+', '-', slug)
            return slug
        return v


# Response schemas
class ResumeResponse(BaseModel):
    """Response schema for resume operations."""
    success: bool
    message: str
    data: Optional[Resume] = None


class ResumeSaveResponse(BaseModel):
    """Response schema for resume save operations."""
    success: bool
    message: str
    errors: Optional[Dict[str, Any]] = None