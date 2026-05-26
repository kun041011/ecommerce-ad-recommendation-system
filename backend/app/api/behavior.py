"""行为追踪路由模块

提供用户行为数据（浏览、点击、收藏、购买等）采集的REST API接口。
采集的行为数据用于推荐系统和用户活跃度计算。
"""

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
    """记录用户行为事件

    将用户的浏览、点击、收藏等行为记录到数据库，
    用于后续推荐算法和活跃度评分。

    参数:
        data: 行为数据（商品ID、行为类型、上下文信息）
        db: 数据库会话
        user: 当前登录用户

    返回:
        dict: 行为记录状态确认
    """
    # 构建行为记录对象并写入数据库
    behavior = UserBehavior(
        user_id=user.id,
        product_id=data.product_id,
        behavior_type=BehaviorType(data.behavior_type),
        context=data.context,
    )
    db.add(behavior)
    db.commit()
    return {"status": "tracked"}
