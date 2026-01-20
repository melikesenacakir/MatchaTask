"""
Data schemas for MatchaTask AI Service
Bu dosya, sistemde kullanılacak veri yapılarını tanımlar.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ExperienceLevel(str, Enum):
    """Yetenek deneyim seviyeleri"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Skill(BaseModel):
    """Tek bir yetenek/yetkinlik"""
    name: str = Field(..., description="Yetenek adı (örn: Python, React)")
    category: Optional[str] = Field(None, description="Kategori (örn: Programming Language, Framework)")
    experience_level: Optional[ExperienceLevel] = Field(None, description="Deneyim seviyesi")
    years_of_experience: Optional[float] = Field(None, ge=0, description="Yıl cinsinden deneyim")
    last_used: Optional[int] = Field(None, description="Son kullanım yılı")


class SkillCard(BaseModel):
    """Bir kullanıcının tüm yeteneklerini içeren kart"""
    user_id: str
    user_name: Optional[str] = None
    skills: List[Skill] = Field(default_factory=list)
    raw_text: Optional[str] = Field(None, description="CV'den çıkarılan ham metin")
    extracted_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "user_name": "John Doe",
                "skills": [
                    {
                        "name": "Python",
                        "category": "Programming Language",
                        "experience_level": "advanced",
                        "years_of_experience": 5.0
                    }
                ]
            }
        }


class TaskRequirement(BaseModel):
    """Görev gereksinimleri"""
    task_id: str
    task_name: str
    required_skills: List[str] = Field(..., description="Gerekli yetenek listesi")
    preferred_skills: Optional[List[str]] = Field(None, description="Tercih edilen yetenekler")
    complexity: Optional[str] = Field(None, description="Görev karmaşıklığı")


class MatchScore(BaseModel):
    """Görev-yetenek eşleşme skoru"""
    user_id: str
    task_id: str
    match_percentage: float = Field(..., ge=0, le=100, description="Eşleşme yüzdesi")
    matched_skills: List[str] = Field(default_factory=list, description="Eşleşen yetenekler")
    missing_skills: List[str] = Field(default_factory=list, description="Eksik yetenekler")
    score_breakdown: Optional[Dict[str, float]] = Field(None, description="Detaylı skor dağılımı")

