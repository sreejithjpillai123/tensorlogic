from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os
import uuid
from datetime import date

app = FastAPI(title="Mini Resume Collector", description="A simple API to collect and manage candidate resumes.", version="1.0.0")

# In-memory database
# Using a list of dictionaries for simplicity
CANDIDATES_DB = []
UPLOAD_DIRECTORY = "uploads"

# Ensure upload directory exists
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
else:
    # Optional: Clean up uploads on restart if desired, but for persistent demo we keep them.
    pass

# Pydantic Model for Response
class Candidate(BaseModel):
    id: str
    full_name: str
    dob: date
    contact_number: str
    contact_address: str
    education_qualification: str
    graduation_year: int
    years_of_experience: float
    skill_set: List[str]
    resume_file_path: str

    class Config:
        orm_mode = True

# Helper to find a candidate by ID
def find_candidate_by_id(candidate_id: str):
    for candidate in CANDIDATES_DB:
        if candidate['id'] == candidate_id:
            return candidate
    return None

@app.post("/candidates/", response_model=Candidate, status_code=201)
async def create_candidate(
    full_name: str = Form(..., description="Full Name of the candidate"),
    dob: date = Form(..., description="Date of Birth (YYYY-MM-DD)"),
    contact_number: str = Form(..., description="Contact Number"),
    contact_address: str = Form(..., description="Physical Address"),
    education_qualification: str = Form(..., description="Highest Qualification"),
    graduation_year: int = Form(..., description="Year of Graduation"),
    years_of_experience: float = Form(..., description="Total Years of Experience"),
    skill_set: str = Form(..., description="Comma-separated list of skills (e.g., Python, C++, SQL)"),
    resume_file: UploadFile = File(..., description="Resume file (PDF, DOC, DOCX)")
):
    # Validate file type
    allowed_content_types = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    if resume_file.content_type not in allowed_content_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, DOC, and DOCX are allowed.")

    # Generate a unique ID for the candidate
    candidate_id = str(uuid.uuid4())
    
    # Save the file
    # We'll use the candidate_id to avoid filename collisions
    file_extension = os.path.splitext(resume_file.filename)[1]
    # Handle weird filenames or missing extensions if necessary, keeping simple for now
    if not file_extension:
        file_extension = ".bin"
        
    saved_filename = f"{candidate_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, saved_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(resume_file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

    # Process skills
    skills_list = [s.strip() for s in skill_set.split(",") if s.strip()]

    candidate_data = {
        "id": candidate_id,
        "full_name": full_name,
        "dob": dob,
        "contact_number": contact_number,
        "contact_address": contact_address,
        "education_qualification": education_qualification,
        "graduation_year": graduation_year,
        "years_of_experience": years_of_experience,
        "skill_set": skills_list,
        "resume_file_path": file_path
    }

    CANDIDATES_DB.append(candidate_data)
    return candidate_data

@app.get("/candidates/", response_model=List[Candidate])
def list_candidates(
    skill: Optional[str] = Query(None, description="Filter by skill (case-insensitive substring match)"),
    min_experience: Optional[float] = Query(None, description="Filter by minimum years of experience"),
    graduation_year: Optional[int] = Query(None, description="Filter by graduation year")
):
    results = CANDIDATES_DB
    
    if skill:
        results = [c for c in results if any(skill.lower() in s.lower() for s in c['skill_set'])]
    
    if min_experience is not None:
        results = [c for c in results if c['years_of_experience'] >= min_experience]
        
    if graduation_year is not None:
        results = [c for c in results if c['graduation_year'] == graduation_year]
        
    return results
@app.get("/health",status_code=200)
def health_check():
    return {"status": "healthy"}


@app.get("/candidates/{candidate_id}", response_model=Candidate)
def get_candidate(candidate_id: str = Path(..., description="The ID of the candidate to retrieve")):
    candidate = find_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@app.delete("/candidates/{candidate_id}", status_code=204)
def delete_candidate(candidate_id: str = Path(..., description="The ID of the candidate to delete")):
    candidate = find_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Remove the file from disk
    if os.path.exists(candidate['resume_file_path']):
        try:
            os.remove(candidate['resume_file_path'])
        except OSError:
            pass # Log error in a real app

    CANDIDATES_DB.remove(candidate)
    return None



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
