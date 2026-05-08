from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_merchant
from app.database import get_db
from app.models.user import User
from app.schemas.ad import AdCreate, AdFetchResponse, AdResponse, AdStatsResponse, ImpressionCreate
from app.services.ad_service import create_ad, fetch_ads_for_user, get_ad_stats, get_merchant_ads, record_impression

router = APIRouter(prefix="/api/ads", tags=["ads"])


@router.post("", response_model=AdResponse, status_code=status.HTTP_201_CREATED)
def create(data: AdCreate, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    return create_ad(db, user.id, **data.dict())


@router.get("/fetch", response_model=AdFetchResponse)
def fetch(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return fetch_ads_for_user(db, user)


@router.post("/impression", status_code=status.HTTP_201_CREATED)
def impression(data: ImpressionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record_impression(db, user.id, data.ad_id, data.impression_type.value, data.context)
    return {"status": "recorded"}


@router.get("/my", response_model=List[AdResponse])
def my_ads(db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    return get_merchant_ads(db, user.id)


@router.get("/{ad_id}/stats", response_model=AdStatsResponse)
def stats(ad_id: int, db: Session = Depends(get_db), _user: User = Depends(require_merchant)):
    return get_ad_stats(db, ad_id)
