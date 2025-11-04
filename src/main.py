from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import uuid
import os

from app.parsers import extract_text_from_file, parse_resume_content
from app.llm_client import LLMClient
from app.models import ParseResultSchema

# 🚨 In-memory storage for parsed resumes (Replace with DB later)
DB = {}

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="AI Resume Parser API",
    version="1.0.0",
    description="AI-powered resume parser with LLM & OCR support."
)

# ✅ API Key auth
API_KEY = os.getenv("API_KEY", "test123")

# ✅ Initialize LLM Client
llm_client = LLMClient()


# ------------------ ✅ HEALTH CHECK ------------------
@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "message": "API is healthy 🚀"}


# ------------------ ✅ UPLOAD & PARSE ------------------
@app.post("/api/v1/resumes/upload")
async def upload_resume(
    file: UploadFile = File(...),
    authorization: str = Header(None)
):
    # ✅ Bearer Token check
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.split(" ")[1]
    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key or token")

    try:
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

        # ✅ Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # ✅ OCR/text extraction
        text = extract_text_from_file(file_path)

        # ✅ Parse with LLM client
        parsed_data = parse_resume_content(text=text, resume_id=file_id, llm_client=llm_client)

        # ✅ Store in memory
        DB[file_id] = parsed_data

        response = ParseResultSchema(
            resume_id=file_id,
            extracted_data=parsed_data
        )

        return JSONResponse(
            content={
                "id": file_id,
                "status": "completed",
                "message": "Resume parsed successfully ✅",
                "data": response.model_dump()
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------ ✅ FETCH PARSED RESUME ------------------
@app.get("/api/v1/resumes/{resume_id}")
async def get_resume(resume_id: str):
    if resume_id not in DB:
        raise HTTPException(status_code=404, detail="Resume not found")
    return DB[resume_id]


# ------------------ ✅ MATCH RESUME TO JOB ------------------
@app.post("/api/v1/resumes/{resume_id}/match")
async def match_resume(resume_id: str, body: dict):
    if resume_id not in DB:
        raise HTTPException(status_code=404, detail="Resume not found")

    job_text = body.get("job_description", "").lower()
    resume = DB[resume_id]

    # Extract skills safely
    skills_list = resume.get("skills", [])
    if not skills_list:
        return {"resume_id": resume_id, "score": 0}

    # Handle both dict format and Skill object format
    skills = set()
    for skill in skills_list:
        if isinstance(skill, dict):
            skill_name = skill.get("skill_name", "")
        else:
            skill_name = getattr(skill, "skill_name", "")
        
        if skill_name:
            skills.add(skill_name.lower())

    score = 0
    if skills:
        matched = sum(1 for s in skills if s in job_text)
        score = round((matched / len(skills)) * 100, 2)

    return {"resume_id": resume_id, "score": score}