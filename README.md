# 🚀 AI-Powered Resume Parser & Job Matcher API

A production-ready **FastAPI** service that extracts structured data from resumes (PDF/DOCX/TXT), enhances fields using AI, and scores resumes against job descriptions.

## ✨ Features

- ✅ Upload & parse resumes
- ✅ Extract skills, experience, education, personal info
- ✅ AI refinement via OpenAI / LLMs (optional)
- ✅ Resume-to-job matching score
- ✅ SQLite storage + pluggable DB layer
- ✅ Test suite included (pytest)
- ✅ Docker support
- ✅ Modular, extensible architecture

---

## ⚙️ Tech Stack

| Component | Tech |
|---|---|
API Framework | FastAPI  
Parsing | pdfminer, python-docx, spaCy  
AI Layer | OpenAI (optional fallback mode)  
Database | SQLite (swappable DB layer)  
Testing | pytest + httpx  
Container | Docker / Compose  

---

## 🚀 Quickstart

### 1️⃣ Setup Environment

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

pip install -r requirements.txt
