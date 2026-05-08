from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from app.models.ad import AdStatus, BidType, ImpressionType


class AdCreate(BaseModel):
    title: str
    content: str = ""
    image_url: str = ""
    target_url: str = ""
    bid_amount: float
    bid_type: BidType = BidType.CPC
    daily_budget: float
    total_budget: float
    target_tags: Optional[List[str]] = None


class AdResponse(BaseModel):
    id: int
    advertiser_id: int
    title: str
    content: str
    image_url: str
    target_url: str
    bid_amount: float
    bid_type: BidType
    daily_budget: float
    total_budget: float
    spent_amount: float
    target_tags: Optional[List[str]] = None
    status: AdStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class AdFetchResponse(BaseModel):
    ads: List[AdResponse]
    frequency_level: str
    remaining_today: int


class ImpressionCreate(BaseModel):
    ad_id: int
    impression_type: ImpressionType
    context: Optional[Dict] = None


class AdStatsResponse(BaseModel):
    ad_id: int
    total_shows: int
    total_clicks: int
    total_converts: int
    ctr: float
    spent: float
