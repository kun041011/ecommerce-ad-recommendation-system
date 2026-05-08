from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.user import AdFrequencyLevel, UserRole


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar_url: Optional[str] = None
    role: UserRole
    activity_score: float
    ad_frequency_level: AdFrequencyLevel
    created_at: datetime
    last_active_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
