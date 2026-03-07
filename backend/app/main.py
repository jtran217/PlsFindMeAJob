from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.api.routes import jobs, generate, resume
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.API_TITLE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router, prefix="/api/v2", tags=["resume"])
app.include_router(jobs.router, prefix="/api", tags=["jobs"])
app.include_router(generate.router, prefix="/api", tags=["generate"])

@app.get("/")
def root():
    """Root endpoint with welcome message."""
    return {"message": "PlsFindMeAJob API is running 🚀"}
