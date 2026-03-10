import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from app.models.resume import Resume, OptimizedResume


class ResumeService:
    """Service for managing resume data with file-based storage"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize ResumeService with data directory
        
        Args:
            data_dir: Directory path for storing resume data (defaults to project data dir)
        """
        if data_dir is None:
            project_root = Path(__file__).parent.parent.parent
            self.data_dir = project_root / "data"
        else:
            self.data_dir = Path(data_dir)
            
        self.resume_file = self.data_dir / "user_resume.json"
        self.versions_dir = self.data_dir / "resume_versions"
        
        self.data_dir.mkdir(exist_ok=True)
        self.versions_dir.mkdir(exist_ok=True)
    
    def load_master_resume(self) -> Resume:
        """
        Load master resume from file, return empty structure if not found
        
        Returns:
            Resume object (empty if no file exists)
        """
        try:
            if self.resume_file.exists():
                with open(self.resume_file, 'r', encoding='utf-8') as f:
                    resume_data = json.load(f)
                return Resume(**resume_data)
            else:
                # Return empty resume structure as requested
                return self.create_empty_resume()
        except (json.JSONDecodeError, ValueError, FileNotFoundError) as e:
            print(f"Error loading resume: {e}")
            # Return empty resume on error
            return self.create_empty_resume()
    
    def save_master_resume(self, resume: Resume) -> bool:
        """
        Save master resume to file with atomic write
        
        Args:
            resume: Resume object to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Convert to dict for JSON serialization
            resume_dict = resume.model_dump()
            
            # Atomic write: write to temp file first, then move
            temp_file = self.resume_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(resume_dict, f, indent=2, ensure_ascii=False)
            
            # Move temp file to actual file (atomic on most filesystems)
            temp_file.replace(self.resume_file)
            
            print(f"Resume saved successfully to {self.resume_file}")
            return True
            
        except Exception as e:
            print(f"Error saving resume: {e}")
            # Clean up temp file if it exists
            temp_file = self.resume_file.with_suffix('.tmp')
            if temp_file.exists():
                temp_file.unlink()
            return False
    
    def load_resume_version(self, job_id: str) -> Optional[OptimizedResume]:
        """
        Load job-specific resume version
        
        Args:
            job_id: Job identifier
            
        Returns:
            OptimizedResume if found, None otherwise
        """
        try:
            version_file = self.versions_dir / f"{job_id}_optimized.json"
            if version_file.exists():
                with open(version_file, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
                return OptimizedResume(**version_data)
            return None
        except Exception as e:
            print(f"Error loading resume version for job {job_id}: {e}")
            return None
    
    def save_resume_version(self, job_id: str, optimized: OptimizedResume) -> bool:
        """
        Save job-specific resume version
        
        Args:
            job_id: Job identifier
            optimized: OptimizedResume object to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            version_file = self.versions_dir / f"{job_id}_optimized.json"
            
            # Update generated timestamp
            optimized.generated_at = datetime.utcnow().isoformat() + "Z"
            
            # Convert to dict for JSON serialization
            version_dict = optimized.model_dump()
            
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(version_dict, f, indent=2, ensure_ascii=False)
            
            print(f"Resume version saved for job {job_id}")
            return True
            
        except Exception as e:
            print(f"Error saving resume version for job {job_id}: {e}")
            return False
    
    def list_resume_versions(self) -> list[str]:
        """
        List all available resume versions
        
        Returns:
            List of job IDs that have resume versions
        """
        try:
            job_ids = []
            for file_path in self.versions_dir.glob("*_optimized.json"):
                # Extract job_id from filename (remove _optimized.json suffix)
                job_id = file_path.stem.replace("_optimized", "")
                job_ids.append(job_id)
            return sorted(job_ids)
        except Exception as e:
            print(f"Error listing resume versions: {e}")
            return []
    
    def create_empty_resume(self) -> Resume:
        """
        Create an empty resume structure with all required fields
        
        Returns:
            Empty Resume object
        """
        from app.models.resume import PersonalInfo, TechnicalSkills
        
        return Resume(
            personal_info=PersonalInfo(
                name="",
                phone="",
                email="",
                linkedin="",
                github=""
            ),
            education=[],
            technical_skills=TechnicalSkills(
                languages=[],
                frameworks=[],
                developer_tools=[],
                libraries=[]
            ),
            experiences=[],
            projects=[]
        )
    
    def delete_resume_version(self, job_id: str) -> bool:
        """
        Delete a job-specific resume version
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            version_file = self.versions_dir / f"{job_id}_optimized.json"
            if version_file.exists():
                version_file.unlink()
                print(f"Resume version deleted for job {job_id}")
                return True
            else:
                print(f"No resume version found for job {job_id}")
                return False
        except Exception as e:
            print(f"Error deleting resume version for job {job_id}: {e}")
            return False
    
    def backup_resume(self) -> bool:
        """
        Create a backup of the current master resume
        
        Returns:
            True if backup created successfully, False otherwise
        """
        try:
            if self.resume_file.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self.data_dir / f"user_resume_backup_{timestamp}.json"
                
                # Copy current resume to backup
                with open(self.resume_file, 'r', encoding='utf-8') as src:
                    with open(backup_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                
                print(f"Resume backup created: {backup_file}")
                return True
            else:
                print("No resume file to backup")
                return False
        except Exception as e:
            print(f"Error creating resume backup: {e}")
            return False
