from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, field_validator


class ReviewCreate(BaseModel):
    product_id: int
    rating: int
    content: str = ""

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: int
    content: str
    helpful_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class QACreate(BaseModel):
    product_id: int
    question: str


class QAAnswerCreate(BaseModel):
    answer: str


class QAResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    question: str
    answer: Optional[str] = None
    answered_by: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class BehaviorTrack(BaseModel):
    product_id: Optional[int] = None
    behavior_type: str
    context: Optional[Dict] = None


class ActivityScoreResponse(BaseModel):
    score: float
    level: str
    ad_frequency_level: str
