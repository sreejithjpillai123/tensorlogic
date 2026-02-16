# Mini Resume Collector Application

A simple REST API built with FastAPI to collect and manage candidate resumes.

## Features

- **Resume Upload**: Upload resumes (PDF, DOC, DOCX) along with candidate details.
- **In-Memory Storage**: Data is stored temporarily in memory (reset on restart).
- **Candidate Listing**: Filter candidates by skill, experience, or graduation year.
- **Candidate Details**: Retrieve full details including the path to the stored resume.
- **Delete Candidate**: Remove candidate data and the associated resume file.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application**:
    ```bash
    python -m uvicorn main:app --reload
    ```
    The server will start at `http://127.0.0.1:8000`.

## API Documentation

FastAPI provides interactive API documentation. Once the server is running, visit:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Endpoints

### 1. Upload Resume
**POST** `/candidates/`

Upload a resume file and provide candidate details as form data.

**Parameters**:
- `full_name`: string
- `dob`: date (YYYY-MM-DD)
- `contact_number`: string
- `contact_address`: string
- `education_qualification`: string
- `graduation_year`: integer
- `years_of_experience`: float
- `skill_set`: string (comma-separated, e.g., "Python, SQL, fastening")
- `resume_file`: file (PDF, DOC, DOCX)

### 2. List Candidates
**GET** `/candidates/`

List all candidates or filter them.

**Query Parameters**:
- `skill`: Filter by skill (case-insensitive substring match).
- `min_experience`: Filter by minimum years of experience.
- `graduation_year`: Filter by graduation year.

### 3. Get Candidate Details
**GET** `/candidates/{candidate_id}`

Retrieve details for a specific candidate by their ID.

### 4. Delete Candidate
**DELETE** `/candidates/{candidate_id}`

Remove a candidate and their uploaded resume file.
