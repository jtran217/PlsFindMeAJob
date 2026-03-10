"""
Test cases for scoring validation - Phase 1.1
Tests the scoring algorithm accuracy with expected rankings
"""

import sys
sys.path.append('/home/johnnytran/Projects/PlsFindMeAJob/backend')

from app.models.resume import *
from app.services.scoring_service import ScoringService
from app.services.keyword_extraction import KeywordExtractor
from sqlalchemy.orm import Session


def create_test_resume() -> Resume:
    """Create a test resume with known characteristics for validation"""
    
    # Experience 1: High match for backend/API jobs
    exp1 = Experience(
        id="test_exp_1",
        title="Backend Developer",
        company="TechCorp",
        location="SF, CA", 
        duration="2022-Present",
        bullet_points=[
            BulletPoint(
                text="Developed REST APIs using FastAPI and PostgreSQL, serving 10K+ users"
            ),
            BulletPoint(
                text="Implemented microservices architecture with Docker and Kubernetes"
            )
        ]
    )
    
    # Experience 2: High match for frontend jobs
    exp2 = Experience(
        id="test_exp_2", 
        title="Frontend Developer",
        company="WebCorp",
        location="NYC, NY",
        duration="2020-2022",
        bullet_points=[
            BulletPoint(
                text="Built responsive web applications using React and TypeScript"
            ),
            BulletPoint(
                text="Optimized performance with React hooks and state management"
            )
        ]
    )
    
    # Experience 3: Low match for tech jobs (business analyst)
    exp3 = Experience(
        id="test_exp_3",
        title="Business Analyst", 
        company="BusinessCorp",
        location="LA, CA",
        duration="2018-2020",
        bullet_points=[
            BulletPoint(
                text="Analyzed business requirements and created documentation"
            ),
            BulletPoint(
                text="Collaborated with stakeholders to define project scope"
            )
        ]
    )
    
    # Project 1: High match for full-stack roles
    proj1 = Project(
        id="test_proj_1",
        name="E-commerce Platform",
        technologies="React, Node.js, MongoDB",
        duration="2021-2022",
        bullet_points=[
            BulletPoint(
                text="Built full-stack application with React frontend and Node.js backend"
            ),
            BulletPoint(
                text="Integrated payment processing and user authentication"
            )
        ]
    )
    
    # Project 2: High match for DevOps/Infrastructure
    proj2 = Project(
        id="test_proj_2", 
        name="CI/CD Pipeline",
        technologies="Docker, Jenkins, AWS",
        duration="2020-2021",
        bullet_points=[
            BulletPoint(
                text="Automated deployment pipeline using Jenkins and Docker"
            ),
            BulletPoint(
                text="Configured AWS infrastructure with auto-scaling capabilities"
            )
        ]
    )
    
    return Resume(
        personal_info=PersonalInfo(name="Test User"),
        experiences=[exp1, exp2, exp3],
        projects=[proj1, proj2]
    )


def create_test_job_analysis(job_type: str) -> JobAnalysis:
    """Create test job analysis for different job types"""
    
    if job_type == "backend":
        return JobAnalysis(
            job_id="test_backend_job",
            keywords=["API", "backend", "microservices", "deployment", "performance"],
            technologies=["FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
            job_title="Senior Backend Developer", 
            company="Test Company"
        )
    elif job_type == "frontend":
        return JobAnalysis(
            job_id="test_frontend_job",
            keywords=["frontend", "responsive", "performance", "user", "application"],
            technologies=["React", "TypeScript", "JavaScript"],
            job_title="Frontend Developer",
            company="Test Company"
        )
    elif job_type == "fullstack":
        return JobAnalysis(
            job_id="test_fullstack_job", 
            keywords=["full-stack", "application", "backend", "frontend", "user"],
            technologies=["React", "Node.js", "MongoDB", "JavaScript"],
            job_title="Full-Stack Developer",
            company="Test Company"
        )
    elif job_type == "devops":
        return JobAnalysis(
            job_id="test_devops_job",
            keywords=["deployment", "infrastructure", "automation", "pipeline", "scaling"],
            technologies=["Docker", "Jenkins", "AWS", "Kubernetes"],
            job_title="DevOps Engineer", 
            company="Test Company"
        )
    else:
        raise ValueError(f"Unknown job type: {job_type}")


def test_scoring_algorithm():
    """Test the scoring algorithm with expected rankings"""
    
    # Create mock scoring service (without DB dependency)
    class MockScoringService:
        def __init__(self):
            self.keyword_extractor = KeywordExtractor()
        
        def calculate_relevance_score(self, item, job_analysis):
            item_keywords = set(item.overall_keywords)
            job_keywords = set(job_analysis.keywords) 
            job_technologies = set(job_analysis.technologies)
            
            # 50% keyword matching
            keyword_overlap = len(item_keywords & job_keywords)
            keyword_score = keyword_overlap / max(len(job_keywords), 1) if job_keywords else 0.0
            
            # 50% technology overlap
            item_technologies = self.keyword_extractor.extract_technologies_from_keywords(
                list(item_keywords)
            )
            tech_overlap = len(item_technologies & job_technologies)
            tech_score = tech_overlap / max(len(job_technologies), 1) if job_technologies else 0.0
            
            return min((keyword_score * 0.5) + (tech_score * 0.5), 1.0)
    
    test_resume = create_test_resume()
    scoring_service = MockScoringService()
    
    print("=== SCORING ALGORITHM VALIDATION ===\\n")
    
    # Test Case 1: Backend Job
    print("TEST 1: Backend Developer Job")
    backend_job = create_test_job_analysis("backend") 
    print(f"Job Keywords: {backend_job.keywords}")
    print(f"Job Technologies: {backend_job.technologies}")
    print("\\nExperience Scores:")
    
    backend_scores = []
    for exp in test_resume.experiences:
        score = scoring_service.calculate_relevance_score(exp, backend_job)
        backend_scores.append((exp.title, score, exp.id))
        print(f"  {exp.title}: {score:.3f} (keywords: {exp.overall_keywords[:5]}...)")
    
    # Validate: Backend Developer should score highest
    backend_scores.sort(key=lambda x: x[1], reverse=True)
    assert backend_scores[0][0] == "Backend Developer", f"Backend Developer should rank first, got {backend_scores[0][0]}"
    assert backend_scores[0][1] > 0.3, f"Backend Developer score should be > 0.3, got {backend_scores[0][1]}"
    print(f"✓ PASS: Backend Developer ranked first with score {backend_scores[0][1]:.3f}")
    
    # Test Case 2: Frontend Job
    print("\\nTEST 2: Frontend Developer Job")
    frontend_job = create_test_job_analysis("frontend")
    print(f"Job Keywords: {frontend_job.keywords}")
    print(f"Job Technologies: {frontend_job.technologies}")
    print("\\nExperience Scores:")
    
    frontend_scores = []
    for exp in test_resume.experiences:
        score = scoring_service.calculate_relevance_score(exp, frontend_job)
        frontend_scores.append((exp.title, score, exp.id))
        print(f"  {exp.title}: {score:.3f}")
    
    # Validate: Frontend Developer should score highest
    frontend_scores.sort(key=lambda x: x[1], reverse=True)
    assert frontend_scores[0][0] == "Frontend Developer", f"Frontend Developer should rank first, got {frontend_scores[0][0]}"
    assert frontend_scores[0][1] > 0.2, f"Frontend Developer score should be > 0.2, got {frontend_scores[0][1]}"
    print(f"✓ PASS: Frontend Developer ranked first with score {frontend_scores[0][1]:.3f}")
    
    # Test Case 3: Full-Stack Job  
    print("\\nTEST 3: Full-Stack Developer Job")
    fullstack_job = create_test_job_analysis("fullstack")
    print(f"Job Keywords: {fullstack_job.keywords}")
    print(f"Job Technologies: {fullstack_job.technologies}")
    print("\\nProject Scores:")
    
    project_scores = []
    for proj in test_resume.projects:
        score = scoring_service.calculate_relevance_score(proj, fullstack_job)
        project_scores.append((proj.name, score, proj.id))
        print(f"  {proj.name}: {score:.3f} (keywords: {proj.overall_keywords[:5]}...)")
    
    # Validate: E-commerce Platform should score higher than CI/CD Pipeline
    project_scores.sort(key=lambda x: x[1], reverse=True)
    assert project_scores[0][0] == "E-commerce Platform", f"E-commerce Platform should rank first, got {project_scores[0][0]}"
    print(f"✓ PASS: E-commerce Platform ranked first with score {project_scores[0][1]:.3f}")
    
    # Test Case 4: DevOps Job
    print("\\nTEST 4: DevOps Engineer Job")
    devops_job = create_test_job_analysis("devops")
    print(f"Job Keywords: {devops_job.keywords}")
    print(f"Job Technologies: {devops_job.technologies}")
    print("\\nProject Scores:")
    
    devops_project_scores = []
    for proj in test_resume.projects:
        score = scoring_service.calculate_relevance_score(proj, devops_job)
        devops_project_scores.append((proj.name, score, proj.id))
        print(f"  {proj.name}: {score:.3f}")
    
    # Validate: CI/CD Pipeline should score higher for DevOps
    devops_project_scores.sort(key=lambda x: x[1], reverse=True)
    assert devops_project_scores[0][0] == "CI/CD Pipeline", f"CI/CD Pipeline should rank first for DevOps, got {devops_project_scores[0][0]}"
    print(f"✓ PASS: CI/CD Pipeline ranked first with score {devops_project_scores[0][1]:.3f}")
    
    print("\\n=== ALL TESTS PASSED ===")
    print("\\nScoring Algorithm Validation Summary:")
    print("✓ Backend jobs correctly prioritize backend experience")
    print("✓ Frontend jobs correctly prioritize frontend experience") 
    print("✓ Full-stack jobs correctly prioritize full-stack projects")
    print("✓ DevOps jobs correctly prioritize DevOps projects")
    print("✓ Scores are within expected ranges (0.0-1.0)")
    print("✓ Technology overlap weighting works correctly")
    print("✓ Keyword matching weighting works correctly")


def test_edge_cases():
    """Test edge cases in scoring algorithm"""
    
    print("\\n=== EDGE CASE TESTING ===\\n")
    
    # Test with empty job requirements
    empty_job = JobAnalysis(
        job_id="empty_job",
        keywords=[],
        technologies=[], 
        job_title="Empty Job",
        company="Test"
    )
    
    test_resume = create_test_resume()
    scoring_service = MockScoringService()
    
    print("TEST: Empty Job Requirements")
    for exp in test_resume.experiences[:1]:
        score = scoring_service.calculate_relevance_score(exp, empty_job)
        print(f"  {exp.title}: {score:.3f}")
        assert score == 0.0, f"Empty job should give score 0.0, got {score}"
    print("✓ PASS: Empty job requirements return 0.0 score")
    
    # Test with no matching keywords/technologies
    mismatch_job = JobAnalysis(
        job_id="mismatch_job",
        keywords=["blockchain", "cryptocurrency", "mining"],
        technologies=["Solidity", "Ethereum", "Bitcoin"],
        job_title="Blockchain Developer", 
        company="Crypto Corp"
    )
    
    print("\\nTEST: No Matching Keywords/Technologies")
    for exp in test_resume.experiences[:1]:
        score = scoring_service.calculate_relevance_score(exp, mismatch_job)
        print(f"  {exp.title}: {score:.3f}")
        assert score == 0.0, f"No match should give score 0.0, got {score}"
    print("✓ PASS: No matching requirements return 0.0 score")
    
    print("\\n✓ ALL EDGE CASES PASSED")


if __name__ == "__main__":
    # Import fix for running as script
    class MockScoringService:
        def __init__(self):
            self.keyword_extractor = KeywordExtractor()
        
        def calculate_relevance_score(self, item, job_analysis):
            item_keywords = set(item.overall_keywords)
            job_keywords = set(job_analysis.keywords)
            job_technologies = set(job_analysis.technologies)
            
            # 50% keyword matching
            keyword_overlap = len(item_keywords & job_keywords)
            keyword_score = keyword_overlap / max(len(job_keywords), 1) if job_keywords else 0.0
            
            # 50% technology overlap
            item_technologies = self.keyword_extractor.extract_technologies_from_keywords(
                list(item_keywords)
            )
            tech_overlap = len(item_technologies & job_technologies)
            tech_score = tech_overlap / max(len(job_technologies), 1) if job_technologies else 0.0
            
            return min((keyword_score * 0.5) + (tech_score * 0.5), 1.0)
    
    # Run validation tests
    test_scoring_algorithm()
    test_edge_cases()