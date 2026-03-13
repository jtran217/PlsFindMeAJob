"""
Resume scoring service for analyzing job-resume relevance.

This module provides functionality to extract job requirements and score
resume items (experiences and projects) based on keyword and technology matching.
"""

import logging
from typing import Dict, List, Optional, Tuple, Set, Union

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.job_models import Job
from app.models.resume import Resume, Experience, Project, JobAnalysis
from app.services.keyword_extraction import KeywordExtractor

# Configure logging
logger = logging.getLogger(__name__)


class ScoringService:
    """Service for scoring resume items against job requirements"""
    
    def __init__(self, db: Session):
        """
        Initialize ScoringService with database session
        
        Args:
            db: SQLAlchemy session for job database access
        """
        self.db = db
        self.keyword_extractor = KeywordExtractor()
    
    def extract_job_requirements(self, job_id: str) -> JobAnalysis:
        """
        Extract keywords and technologies from job description.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            JobAnalysis object containing extracted keywords and technologies
            
        Raises:
            ValueError: If job with given ID is not found
            SQLAlchemyError: If database query fails
        """
        try:
            logger.info(f"Extracting requirements for job {job_id}")
            
            # Query job from database
            job = self.db.query(Job).filter(Job.id == job_id).first()
            if not job:
                logger.warning(f"Job with ID {job_id} not found")
                raise ValueError(f"Job with ID {job_id} not found")
            
            # Safely combine job text fields
            job_text_parts = []
            if job.description is not None:
                job_text_parts.append(str(job.description))
            if job.skills is not None:
                job_text_parts.append(str(job.skills))
            if job.title is not None:
                job_text_parts.append(str(job.title))
            
            job_text = " ".join(job_text_parts)
            
            if not job_text.strip():
                logger.warning(f"Job {job_id} has no extractable text content")
            
            # Extract and categorize keywords
            all_keywords = self.keyword_extractor.extract_keywords(job_text)
            technologies = self.keyword_extractor.extract_technologies_from_keywords(all_keywords)
            general_keywords = [kw for kw in all_keywords if kw not in technologies]
            
            logger.info(f"Extracted {len(general_keywords)} keywords and {len(technologies)} technologies for job {job_id}")
            
            return JobAnalysis(
                job_id=job_id,
                keywords=general_keywords,
                technologies=list(technologies),
                job_title=str(job.title) if job.title is not None else "",
                company=str(job.company) if job.company is not None else "",
                job_description=str(job.description) if job.description is not None else "",
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching job {job_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error extracting job requirements for {job_id}: {e}")
            raise
    
    def calculate_relevance_score(
        self, 
        item: Union[Experience, Project], 
        job_analysis: JobAnalysis
    ) -> float:
        """
        Calculate relevance score using simplified 2-factor algorithm.
        
        Uses 50% keyword matching + 50% technology overlap scoring.
        
        Args:
            item: Experience or Project to score
            job_analysis: Job requirements analysis
            
        Returns:
            Relevance score from 0.0 to 1.0
            
        Raises:
            AttributeError: If item doesn't have required keywords property
        """
        try:
            # Validate inputs
            if not job_analysis:
                logger.warning("Empty job analysis provided for scoring")
                return 0.0
            
            # Extract item keywords (computed property aggregates bullet points)
            item_keywords = set(item.overall_keywords)
            job_keywords = set(job_analysis.keywords)
            job_technologies = set(job_analysis.technologies)
            
            if not item_keywords:
                logger.debug(f"Item {getattr(item, 'id', 'unknown')} has no keywords")
                return 0.0
            
            # Factor 1: General keyword matching (50% weight)
            keyword_overlap = len(item_keywords & job_keywords)
            keyword_score = (
                keyword_overlap / len(job_keywords) 
                if job_keywords 
                else 0.0
            )
            
            # Factor 2: Technology overlap (50% weight) 
            item_technologies = self.keyword_extractor.extract_technologies_from_keywords(
                list(item_keywords)
            )
            tech_overlap = len(item_technologies & job_technologies)
            tech_score = (
                tech_overlap / len(job_technologies) 
                if job_technologies 
                else 0.0
            )
            
            # Combine scores with equal weighting
            final_score = (keyword_score * 0.5) + (tech_score * 0.5)
            
            # Ensure score doesn't exceed 1.0
            return min(final_score, 1.0)
            
        except AttributeError as e:
            logger.error(f"Item missing required attributes for scoring: {e}")
            return 0.0
        except Exception as e:
            logger.error(f"Unexpected error calculating relevance score: {e}")
            return 0.0
    
    def rank_experiences_and_projects(
        self, 
        resume: Resume, 
        job_analysis: JobAnalysis
    ) -> Tuple[List[Experience], List[Project]]:
        """
        Score and rank all experiences and projects by relevance.
        
        Args:
            resume: Resume object containing experiences and projects
            job_analysis: Job requirements analysis
            
        Returns:
            Tuple of (ranked_experiences, ranked_projects) sorted by score descending
        """
        try:
            logger.info(f"Ranking resume items for job {job_analysis.job_id}")
            
            # Score and rank experiences
            scored_experiences = []
            for experience in resume.experiences:
                score = self.calculate_relevance_score(experience, job_analysis)
                experience.relevance_score = score
                scored_experiences.append(experience)
            
            ranked_experiences = sorted(
                scored_experiences, 
                key=lambda x: x.relevance_score, 
                reverse=True
            )
            
            # Score and rank projects
            scored_projects = []
            for project in resume.projects:
                score = self.calculate_relevance_score(project, job_analysis)
                project.relevance_score = score
                scored_projects.append(project)
            
            ranked_projects = sorted(
                scored_projects, 
                key=lambda x: x.relevance_score, 
                reverse=True
            )
            
            logger.info(f"Ranked {len(ranked_experiences)} experiences and {len(ranked_projects)} projects")
            return ranked_experiences, ranked_projects
            
        except Exception as e:
            logger.error(f"Error ranking resume items: {e}")
            return [], []
    
    def get_top_selections(
        self,
        ranked_experiences: List[Experience],
        ranked_projects: List[Project],
        max_experiences: int = 3,
        max_projects: int = 2
    ) -> Tuple[List[str], List[str]]:
        """
        Get top experience and project IDs for resume optimization.
        
        Args:
            ranked_experiences: Experiences sorted by relevance score (descending)
            ranked_projects: Projects sorted by relevance score (descending)
            max_experiences: Maximum number of experiences to select
            max_projects: Maximum number of projects to select
            
        Returns:
            Tuple of (experience_ids, project_ids) for top selections
        """
        top_experience_ids = [
            exp.id for exp in ranked_experiences[:max_experiences]
        ]
        
        top_project_ids = [
            proj.id for proj in ranked_projects[:max_projects] 
        ]
        
        logger.debug(f"Selected top {len(top_experience_ids)} experiences and {len(top_project_ids)} projects")
        return top_experience_ids, top_project_ids
    
    def analyze_job_match_quality(
        self,
        job_analysis: JobAnalysis,
        resume: Resume
    ) -> Dict[str, Union[int, float]]:
        """
        Analyze overall job-resume match quality and provide metrics.
        
        Args:
            job_analysis: Job requirements analysis
            resume: Resume to analyze
            
        Returns:
            Dictionary containing match analysis metrics including:
            - total_items: Total number of experiences and projects
            - avg_relevance_score: Average relevance score across all items
            - max_relevance_score: Highest relevance score found
            - high_relevance_items: Count of items with score >= 0.7
            - medium_relevance_items: Count of items with score 0.3-0.7
            - low_relevance_items: Count of items with score < 0.3
            - job_keywords_count: Number of keywords extracted from job
            - job_technologies_count: Number of technologies extracted from job
        """
        try:
            ranked_exp, ranked_proj = self.rank_experiences_and_projects(resume, job_analysis)
            
            # Collect all relevance scores
            exp_scores = [exp.relevance_score for exp in ranked_exp]
            proj_scores = [proj.relevance_score for proj in ranked_proj]
            all_scores = exp_scores + proj_scores
            
            if not all_scores:
                logger.warning("No items found for match quality analysis")
                return {
                    "total_items": 0,
                    "avg_relevance_score": 0.0,
                    "max_relevance_score": 0.0,
                    "high_relevance_items": 0,
                    "medium_relevance_items": 0,
                    "low_relevance_items": 0,
                    "job_keywords_count": len(job_analysis.keywords),
                    "job_technologies_count": len(job_analysis.technologies)
                }
            
            # Calculate comprehensive metrics
            analysis = {
                "total_items": len(all_scores),
                "avg_relevance_score": sum(all_scores) / len(all_scores),
                "max_relevance_score": max(all_scores),
                "high_relevance_items": len([s for s in all_scores if s >= 0.7]),
                "medium_relevance_items": len([s for s in all_scores if 0.3 <= s < 0.7]),
                "low_relevance_items": len([s for s in all_scores if s < 0.3]),
                "job_keywords_count": len(job_analysis.keywords),
                "job_technologies_count": len(job_analysis.technologies)
            }
            
            logger.info(f"Match analysis complete: {analysis['high_relevance_items']} high relevance items")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing job match quality: {e}")
            return {
                "total_items": 0,
                "avg_relevance_score": 0.0,
                "max_relevance_score": 0.0,
                "high_relevance_items": 0,
                "medium_relevance_items": 0,
                "low_relevance_items": 0,
                "job_keywords_count": 0,
                "job_technologies_count": 0
            }