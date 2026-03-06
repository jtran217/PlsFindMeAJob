from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.api.routes import profiles, jobs, generate
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(title=settings.API_TITLE)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(profiles.router, prefix="/api", tags=["profiles"])
app.include_router(jobs.router, prefix="/api", tags=["jobs"])
app.include_router(generate.router, prefix="/api", tags=["generate"])
@app.get("/")
def root():
    """Root endpoint with welcome message."""
    return {"message": "PlsFindMeAJob API is running 🚀"}
    
