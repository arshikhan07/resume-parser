# Resume Parser Architecture

## Overview
The Resume Parser is an AI-integrated FastAPI microservice that extracts structured data from resumes (PDF, DOCX, TXT) and returns JSON-formatted candidate profiles with skills, experience, education, and contact info.

------------------------------------------------------------

## System Components

### 1. FastAPI Backend (src/main.py)
- Handles API routes (upload, parse, match)
- Coordinates parsing + AI extraction workflow

### 2. File Parser (src/parsers.py)
- Reads resumes in PDF/DOCX/TXT formats
- Converts documents into clean text
- Uses pdfminer / pypdf / docx2txt

### 3. LLM Client (src/llm_client.py)
- Sends extracted text to OpenAI or local LLM
- Returns structured resume JSON
- Works with/without an API key (fallback mode)

### 4. Database Layer (PostgreSQL / SQLite)
- Stores uploaded files + parsed metadata
- ORM or raw SQL migrations
- Used for retrieving parsed results later

### 5. Models (src/models.py)
- Pydantic schemas
- Ensures strict, typed JSON response format

------------------------------------------------------------

## System Architecture Diagram (ASCII)

                ┌──────────────┐
                │    Client    │
                └──────┬───────┘
                       │ Upload Resume
                       ▼
               ┌───────────────┐
               │   FastAPI     │
               └──────┬────────┘
       Save File      │      Parse + Send to LLM
                       ▼
             ┌──────────────────┐
             │ File Extractor   │
             └──────┬───────────┘
                    │ Raw Text
                    ▼
            ┌────────────────────┐
            │   AI / LLM Engine  │
            └─────────┬──────────┘
                      │ Parsed JSON
                      ▼
          ┌────────────────────────┐
          │  Database (Parsed CVs) │
          └─────────┬──────────────┘
                    ▼
             ✅ Structured Output

------------------------------------------------------------

## Sequence Flow

1. User uploads resume `/upload`
2. Service stores file
3. Parser extracts plain text
4. Text sent to AI model (optional)
5. AI returns structured fields
6. Store structured data in DB
7. Respond with json payload

------------------------------------------------------------

## Entity Relationship Diagram (ERD)

┌──────────────┐        ┌──────────────┐
│   Resume     │        │  ParsedData  │
├──────────────┤        ├──────────────┤
│ id (PK)      │ 1 ───► │ resume_id FK │
│ filename     │        │ json_data    │
│ raw_text     │        │ skills       │
│ created_at   │        │ experience   │
└──────────────┘        │ education    │
                        │ email        │
                        └──────────────┘

------------------------------------------------------------

## Folder Structure

app/
 ├── main.py                 
 ├── routers/                
 ├── parsers/                
 ├── services/               
 ├── db/                     
 ├── models/                 
 ├── utils/                  
 └── tests/                  

migrations/
 └── 001_create_resume_schema.sql

.env.example
requirements.txt
Dockerfile
README.md

------------------------------------------------------------

## Notes
- FastAPI backend orchestrates parsing + AI
- Local DB persists results
- Modular architecture → replace LLM / DB anytime
- Test suite included

------------------------------------------------------------
