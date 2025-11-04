# app/parsers.py
from pathlib import Path
from typing import Any, Dict, List, Optional
import re
import io

from .models import (
    ResumeResponse,
    PersonalInfo,
    ContactInfo,
    WorkExperience,
    Education,
    Skill,
)

from .llm_client import LLMClient

# Text extraction
from pdfminer.high_level import extract_text as pdf_extract_text
import docx

# OCR (optional)
try:
    import pytesseract
    from PIL import Image
    OCR_ENABLED = True
except ImportError:
    OCR_ENABLED = False

# spaCy for NER
import spacy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = spacy.blank("en")

EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_RE = re.compile(r"(\+\d{1,3}[-.\s]?)?(\d{10,12})")


# ------------------------------------------------------------
# File Text Extractors
# ------------------------------------------------------------
def extract_text_from_pdf(path: Path) -> str:
    try:
        return pdf_extract_text(str(path))
    except Exception:
        return ""


def extract_text_from_docx(path: Path) -> str:
    try:
        doc = docx.Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs]
        return "\n".join(paragraphs)
    except Exception:
        return ""


def extract_text_from_image(path: Path) -> str:
    if not OCR_ENABLED:
        return ""
    try:
        img = Image.open(str(path))
        return pytesseract.image_to_string(img)
    except Exception:
        return ""


def extract_text_from_file(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        text = extract_text_from_pdf(path)
        if text.strip() == "" and OCR_ENABLED:
            text = extract_text_from_image(path)
        return text

    elif suffix in (".docx", ".doc"):
        return extract_text_from_docx(path)

    elif suffix in (".jpg", ".jpeg", ".png"):
        return extract_text_from_image(path)

    else:
        return path.read_text(encoding="utf-8", errors="ignore")


# ------------------------------------------------------------
# Basic Extraction Helpers
# ------------------------------------------------------------
def extract_contact(text: str) -> Dict[str, Optional[str]]:
    email = EMAIL_RE.search(text)
    phone = PHONE_RE.search(text)

    top_lines = "\n".join(text.splitlines()[:8])
    doc = nlp(top_lines)

    name = None
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break

    location = None
    for ent in nlp(text[:500]).ents:
        if ent.label_ in ("GPE", "LOC"):
            location = ent.text
            break

    return {
        "full_name": name,
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "location": location,
    }


def extract_skills(text: str) -> List[str]:
    default_skills = [
        "python", "java", "c++", "sql", "aws", "docker", "kubernetes",
        "nlp", "machine learning", "deep learning", "react", "node"
    ]
    text_low = text.lower()
    return sorted({s for s in default_skills if s in text_low})


def extract_experience(text: str) -> List[WorkExperience]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    experiences = []

    for i, line in enumerate(lines):
        if re.search(r"\b(20|19)\d{2}\b", line):
            desc = " ".join(lines[i + 1:i + 4])
            experiences.append(
                WorkExperience(
                    title=line,
                    company=None,
                    description=desc,
                    current=False
                )
            )

    return experiences


def extract_education(text: str) -> List[Education]:
    edu_keywords = ["B.Tech", "Bachelor", "Masters", "BSc", "MSc", "PhD", "Graduation"]
    lines = text.splitlines()

    education = []
    for line in lines:
        for kw in edu_keywords:
            if kw.lower() in line.lower():
                education.append(Education(degree=line))
                break

    return education


# ------------------------------------------------------------
# Main Parse Function
# ------------------------------------------------------------
def parse_resume_content(
    text: str,
    resume_id: str,
    llm_client: Optional[LLMClient] = None
) -> Dict[str, Any]:

    contact = extract_contact(text)
    skills = extract_skills(text)
    experience = extract_experience(text)
    education = extract_education(text)

    parsed = ResumeResponse(
        id=resume_id,
        personalInfo=PersonalInfo(
            full_name=contact["full_name"],
            contact=ContactInfo(
                email=contact["email"],
                phone=contact["phone"],
                address=None,
                linkedin=None,
                website=None
            )
        ),
        experience=experience,
        education=education,
        skills=[Skill(skill_name=s) for s in skills],
        metadata={"raw_length": len(text)},
    ).model_dump()

    if llm_client and llm_client.is_available():
        try:
            refined = llm_client.refine_parsed_resume(parsed)
            parsed.update(refined)
        except Exception:
            pass

    parsed["raw_text"] = text
    return parsed