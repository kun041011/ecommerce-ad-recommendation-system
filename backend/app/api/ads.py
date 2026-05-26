"""广告路由模块

提供广告创建、广告投放获取、曝光记录、商家广告列表和广告统计的REST API接口。
"""

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
    """创建广告接口（仅商家可用）

    Args:
        data: 广告信息（标题、内容、预算等）
        db: 数据库会话
        user: 当前商家用户（需商家权限）

    Returns:
        Ad: 创建成功的广告信息
    """
    return create_ad(db, user.id, **data.dict())


@router.get("/fetch", response_model=AdFetchResponse)
def fetch(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """获取当前用户的广告推荐

    根据用户活跃度和行为数据，个性化推荐广告内容。

    Args:
        db: 数据库会话
        user: 当前登录用户

    Returns:
        AdFetchResponse: 推荐的广告列表
    """
    return fetch_ads_for_user(db, user)


@router.post("/impression", status_code=status.HTTP_201_CREATED)
def impression(data: ImpressionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """记录广告曝光或点击事件

    Args:
        data: 曝光数据（广告ID、曝光类型、上下文）
        db: 数据库会话
        user: 当前登录用户

    Returns:
        dict: 记录状态确认
    """
    # 记录广告曝光/点击到数据库
    record_impression(db, user.id, data.ad_id, data.impression_type.value, data.context)
    return {"status": "recorded"}


@router.get("/my", response_model=List[AdResponse])
def my_ads(db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    """获取当前商家创建的广告列表

    Args:
        db: 数据库会话
        user: 当前商家用户（需商家权限）

    Returns:
        list[Ad]: 当前商家的所有广告
    """
    return get_merchant_ads(db, user.id)


@router.get("/{ad_id}/stats", response_model=AdStatsResponse)
def stats(ad_id: int, db: Session = Depends(get_db), _user: User = Depends(require_merchant)):
    """获取指定广告的统计数据（仅商家可用）

    Args:
        ad_id: 广告ID
        db: 数据库会话
        _user: 当前商家用户（用于权限校验）

    Returns:
        AdStatsResponse: 广告的展示量、点击量、点击率等统计
    """
    return get_ad_stats(db, ad_id)
