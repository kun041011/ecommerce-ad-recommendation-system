"""活跃度路由模块

提供用户活跃度评分查询的REST API接口。
活跃度评分基于用户历史行为数据计算，用于广告频率调控。
"""

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
    """获取当前用户的活跃度评分

    从数据库查询用户所有行为记录，计算活跃度评分并分类等级。
    评分结果同时用于决定广告投放频率。

    Args:
        db: 数据库会话
        user: 当前登录用户

    Returns:
        ActivityScoreResponse: 包含评分、活跃等级和广告频率等级
    """
    # 查询用户所有行为记录
    behaviors = db.query(UserBehavior).filter(UserBehavior.user_id == user.id).all()
    # 将行为记录转换为评分函数需要的字典格式
    behavior_dicts = [{"behavior_type": b.behavior_type.value, "created_at": b.created_at} for b in behaviors]
    # 计算活跃度评分和等级
    score = calculate_activity_score(behavior_dicts)
    level = classify_activity_level(score)
    return ActivityScoreResponse(score=score, level=level, ad_frequency_level=level)
