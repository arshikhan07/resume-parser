"""
models.py

Pydantic models for the Resume Parser API responses and internal structured resume representation.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


# -----------------------------------------------------
# ✅ Resume Parsing Result Schema (used in API responses)
# -----------------------------------------------------
class ParseResultSchema(BaseModel):
    """
    A lightweight wrapper used for API responses when returning parse results.
    """
    resume_id: str = Field(..., description="Unique ID of the uploaded resume")
    extracted_data: Dict[str, Any] = Field(
        ...,
        description="Structured resume data extracted by AI/LLM (use ResumeResponse for a full schema)"
    )


# -----------------------------------------------------
# ✅ Detailed Resume Data Models (future-ready)
# -----------------------------------------------------
class Address(BaseModel):
    """Postal address details (best-effort extraction)."""
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = None
    country: Optional[str] = None


class ContactInfo(BaseModel):
    """Contact methods discovered on the resume."""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[Address] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None


class PersonalInfo(BaseModel):
    """Basic personal name and contact grouping."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    contact: Optional[ContactInfo] = None


class WorkExperience(BaseModel):
    """
    Single work experience entry.
    Use consistent date formats (ISO 8601 recommended) for start_date/end_date if possible.
    """
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None  # ISO date string recommended, e.g. "2020-06-01"
    end_date: Optional[str] = None    # None if current role or unknown
    current: Optional[bool] = False
    description: Optional[str] = None
    achievements: Optional[List[str]] = None
    technologies: Optional[List[str]] = None


class Education(BaseModel):
    """Single education entry."""
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    institution: Optional[str] = None
    location: Optional[str] = None
    graduation_date: Optional[str] = None  # ISO date string recommended, e.g. "2022-05-15"
    gpa: Optional[float] = None
    honors: Optional[List[str]] = None


class Skill(BaseModel):
    """Normalized skill representation (you can map raw tokens to this form)."""
    skill_name: str
    skill_category: Optional[str] = None
    proficiency_level: Optional[str] = None  # e.g., "Beginner", "Intermediate", "Expert"
    years_of_experience: Optional[int] = None
    is_primary: Optional[bool] = False


class AIEnhancements(BaseModel):
    """
    Additional fields produced by AI / LLM post-processing:
    - quality_score, completeness_score: integer heuristics (0-100)
    - suggestions: textual improvement tips
    - industry_fit: scoring across possible industries (e.g. {"FinTech": 0.82})
    """
    quality_score: Optional[int] = None
    completeness_score: Optional[int] = None
    suggestions: Optional[List[str]] = None
    industry_fit: Optional[Dict[str, float]] = None


class ResumeResponse(BaseModel):
    """
    Full structured resume representation. This is what you would typically persist in the DB
    and return from an API endpoint that returns parsed & enriched resume content.
    """
    id: str
    metadata: Optional[Dict[str, Any]] = None  # file size, original filename, parser version, etc.
    personalInfo: Optional[PersonalInfo] = None
    experience: Optional[List[WorkExperience]] = None
    education: Optional[List[Education]] = None
    skills: Optional[List[Skill]] = None
    aiEnhancements: Optional[AIEnhancements] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# -----------------------------------------------------
# ✅ Standard API Error Schema
# -----------------------------------------------------
class ErrorResponse(BaseModel):
    """
    Standardized API error response.
    """
    status: str = Field("error", description="Status of the response; 'error' for failures")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional structured details for debugging or machine parsing"
    )


__all__ = [
    "ParseResultSchema",
    "Address",
    "ContactInfo",
    "PersonalInfo",
    "WorkExperience",
    "Education",
    "Skill",
    "AIEnhancements",
    "ResumeResponse",
    "ErrorResponse",
]