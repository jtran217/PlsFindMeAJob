from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json

models.Base.metadata.create_all(bind=engine)

BASE_DIR = Path(__file__).resolve().parent.parent
PROFILE_PATH = BASE_DIR / "data" / "profile.json"


app = FastAPI(title="PlsFindMeAJob API")

origins = [
    "http://localhost:5173",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.get("/")
def root():
    return {"message": "PlsFindMeAJob API is running 🚀"}

@app.get("/api/jobs")
def get_jobs(skip:int = 0, limit:int = 15, db:Session = Depends(get_db)):
    total = db.query(models.Job).count()
    jobs = db.query(models.Job).offset(skip).limit(limit).all()

    return {
     "total": total,
     "data": jobs
    }

@app.get("/api/profile")
def get_profiles():
    with open(PROFILE_PATH, "r") as f:
        profiles = json.load(f)
    return profiles


@app.post("/api/profile")
def save_profile(profile: dict):
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)
    return {"message":"Profile saved"}
    
