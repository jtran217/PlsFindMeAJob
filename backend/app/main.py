from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)




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
