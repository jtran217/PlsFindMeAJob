"""
Database migration script to add the resume_jobs table.
Run this script to create the new table for RxResume integration.
"""
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.database import DATABASE_URL, Base
from app.models.database import Job, ResumeJob
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_resume_jobs_table():
    """Create the resume_jobs table if it doesn't exist."""
    try:
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        
        # Create the table using SQLAlchemy
        Base.metadata.create_all(bind=engine)
        
        logger.info("Successfully created resume_jobs table")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create resume_jobs table: {e}")
        return False


def verify_table_creation():
    """Verify that the resume_jobs table was created successfully."""
    try:
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='resume_jobs'"))
            table_info = result.fetchone()
            
            if table_info:
                logger.info("✓ resume_jobs table exists")
                logger.info(f"Table structure: {table_info[0]}")
                
                count_result = conn.execute(text("SELECT COUNT(*) FROM resume_jobs"))
                count = count_result.fetchone()[0]
                logger.info(f"✓ Table has {count} records")
                
                return True
            else:
                logger.error("✗ resume_jobs table does not exist")
                return False
                
    except Exception as e:
        logger.error(f"Failed to verify table creation: {e}")
        return False


def main():
    """Main migration function."""
    logger.info("Starting database migration for RxResume integration...")
    
    if create_resume_jobs_table():
        logger.info("✓ Database migration completed successfully")
        
        if verify_table_creation():
            logger.info("✓ Table verification passed")
        else:
            logger.error("✗ Table verification failed")
            return False
    else:
        logger.error("✗ Database migration failed")
        return False
    
    logger.info("Migration completed successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
