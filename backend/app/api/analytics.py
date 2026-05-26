"""数据分析路由模块

提供管理员数据看板、用户活跃度分布和广告效果分析的REST API接口。
所有接口均需管理员权限。
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.api.deps import require_admin
from app.database import get_db
from app.models.ad import Ad, AdImpression, ImpressionType
from app.models.order import Order
from app.models.product import Product
from app.models.user import User

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), _user: User = Depends(require_admin)):
    """管理员数据看板接口

    汇总平台核心运营指标，包括用户数、商品数、订单数、
    营收、广告收入、点击率（CTR）和千次展示收入（RPM）。

    参数:
        db: 数据库会话
        _user: 当前管理员用户（用于权限校验）

    返回:
        dict: 平台核心运营指标汇总
    """
    # 统计用户总数
    total_users = db.query(func.count(User.id)).scalar()
    # 统计商品总数
    total_products = db.query(func.count(Product.id)).scalar()
    # 统计订单总数
    total_orders = db.query(func.count(Order.id)).scalar()
    # 统计订单总营收
    total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0
    # 统计广告总收入
    total_ad_revenue = db.query(func.sum(Ad.spent_amount)).scalar() or 0
    # 统计广告展示总次数
    total_shows = db.query(func.count(AdImpression.id)).filter(AdImpression.impression_type == ImpressionType.show).scalar()
    # 统计广告点击总次数
    total_clicks = db.query(func.count(AdImpression.id)).filter(AdImpression.impression_type == ImpressionType.click).scalar()
    # 计算点击率（CTR）和千次展示收入（RPM）
    ctr = total_clicks / total_shows if total_shows > 0 else 0
    rpm = total_ad_revenue / total_shows * 1000 if total_shows > 0 else 0
    return {
        "total_users": total_users, "total_products": total_products,
        "total_orders": total_orders, "total_revenue": round(total_revenue, 2),
        "total_ad_revenue": round(total_ad_revenue, 2),
        "ctr": round(ctr, 4), "rpm": round(rpm, 2),
    }


@router.get("/activity-dist")
def activity_dist(db: Session = Depends(get_db), _user: User = Depends(require_admin)):
    """用户活跃度分布统计接口

    将用户按活跃度评分分为低活跃（<20）、正常（20-60）、高活跃（>=60）三档。

    参数:
        db: 数据库会话
        _user: 当前管理员用户（用于权限校验）

    返回:
        dict: 各活跃等级的用户数量（low、normal、high）
    """
    # 低活跃用户：评分 < 20
    low = db.query(func.count(User.id)).filter(User.activity_score < 20).scalar()
    # 正常活跃用户：20 <= 评分 < 60
    normal = db.query(func.count(User.id)).filter(User.activity_score >= 20, User.activity_score < 60).scalar()
    # 高活跃用户：评分 >= 60
    high = db.query(func.count(User.id)).filter(User.activity_score >= 60).scalar()
    return {"low": low, "normal": normal, "high": high}


@router.get("/ad-performance")
def ad_performance(db: Session = Depends(get_db), _user: User = Depends(require_admin)):
    """广告效果分析接口

    统计每个广告的展示次数、点击次数、点击率和花费金额。

    参数:
        db: 数据库会话
        _user: 当前管理员用户（用于权限校验）

    返回:
        list[dict]: 每个广告的效果统计数据
    """
    # 查询所有广告
    ads = db.query(Ad).all()
    result = []
    for ad in ads:
        # 统计该广告的展示次数
        shows = db.query(func.count(AdImpression.id)).filter(
            AdImpression.ad_id == ad.id, AdImpression.impression_type == ImpressionType.show
        ).scalar()
        # 统计该广告的点击次数
        clicks = db.query(func.count(AdImpression.id)).filter(
            AdImpression.ad_id == ad.id, AdImpression.impression_type == ImpressionType.click
        ).scalar()
        # 计算点击率并汇总广告效果数据
        result.append({
            "ad_id": ad.id, "title": ad.title, "shows": shows, "clicks": clicks,
            "ctr": round(clicks / shows, 4) if shows > 0 else 0, "spent": ad.spent_amount,
        })
    return result
