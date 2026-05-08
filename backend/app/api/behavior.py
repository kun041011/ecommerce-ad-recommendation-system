from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.behavior import BehaviorType, UserBehavior
from app.models.user import User
from app.schemas.community import BehaviorTrack

router = APIRouter(prefix="/api/behavior", tags=["behavior"])


@router.post("/track", status_code=status.HTTP_201_CREATED)
def track(data: BehaviorTrack, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    behavior = UserBehavior(
        user_id=user.id,
        product_id=data.product_id,
        behavior_type=BehaviorType(data.behavior_type),
        context=data.context,
    )
    db.add(behavior)
    db.commit()
    return {"status": "tracked"}
