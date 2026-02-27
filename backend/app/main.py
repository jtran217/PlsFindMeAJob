from fastapi import FastAPI, Depends, HTTPException


app = FastAPI(title="PlsFindMeAJob API")

@app.get("/")
def root():
    return {"message": "PlsFindMeAJob API is running 🚀"}


