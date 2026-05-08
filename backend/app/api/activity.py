from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.activity.scorer import calculate_activity_score, classify_activity_level
from app.api.deps import get_current_user
from app.database import get_db
from app.models.behavior import UserBehavior
from app.models.user import User
from app.schemas.community import ActivityScoreResponse

router = APIRouter(prefix="/api/activity", tags=["activity"])


@router.get("/my-score", response_model=ActivityScoreResponse)
def my_score(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    behaviors = db.query(UserBehavior).filter(UserBehavior.user_id == user.id).all()
    behavior_dicts = [{"behavior_type": b.behavior_type.value, "created_at": b.created_at} for b in behaviors]
    score = calculate_activity_score(behavior_dicts)
    level = classify_activity_level(score)
    return ActivityScoreResponse(score=score, level=level, ad_frequency_level=level)
