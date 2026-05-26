"""广告投放服务模块

整合活跃度评分、频控、竞价和计费组件，提供完整的广告投放业务逻辑，
包括广告创建、用户广告获取、曝光/点击记录和统计分析。
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.activity.scorer import calculate_activity_score, classify_activity_level
from app.ad_engine.bidding import rank_ads_by_ecpm
from app.ad_engine.billing import calculate_cpc_charge
from app.ad_engine.frequency import FrequencyController
from app.models.ad import Ad, AdImpression, AdStatus, ImpressionType
from app.models.behavior import UserBehavior
from app.models.user import User

# 全局频率控制器实例
freq_controller = FrequencyController()


def create_ad(db: Session, advertiser_id: int, **kwargs) -> Ad:
    """创建新广告

    Args:
        db: 数据库会话
        advertiser_id: 广告主ID
        **kwargs: 广告属性（标题、预算、出价等）

    Returns:
        Ad: 创建完成的广告对象
    """
    ad = Ad(advertiser_id=advertiser_id, **kwargs)
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad


def fetch_ads_for_user(db: Session, user: User) -> dict:
    """为用户获取个性化广告列表

    完整流程：计算活跃度 -> 频控检查 -> 竞价排序 -> 返回结果。

    Args:
        db: 数据库会话
        user: 当前用户对象

    Returns:
        dict: 包含 ads（广告列表）、frequency_level（频控等级）、remaining_today（今日剩余量）
    """
    # 获取用户行为记录，计算活跃度评分和等级
    behaviors = db.query(UserBehavior).filter(UserBehavior.user_id == user.id).all()
    behavior_dicts = [{"behavior_type": b.behavior_type.value, "created_at": b.created_at} for b in behaviors]
    score = calculate_activity_score(behavior_dicts)
    level = classify_activity_level(score)

    # 查询今日已展示次数
    today_count = db.query(AdImpression).filter(
        AdImpression.user_id == user.id,
        AdImpression.impression_type == ImpressionType.show,
    ).count()

    # 查询最近一次展示时间戳
    last_impression = db.query(AdImpression).filter(
        AdImpression.user_id == user.id,
        AdImpression.impression_type == ImpressionType.show,
    ).order_by(AdImpression.created_at.desc()).first()
    last_ts = last_impression.created_at.timestamp() if last_impression else 0

    # 频控检查，不满足条件则返回空列表
    freq_result = freq_controller.check(user.id, level, today_count, last_ts)
    if not freq_result["allowed"]:
        return {"ads": [], "frequency_level": level, "remaining_today": 0}

    # 获取所有生效广告，按eCPM竞价排序后截取
    active_ads = db.query(Ad).filter(Ad.status == AdStatus.active).all()
    ad_dicts = [
        {"id": a.id, "bid_amount": a.bid_amount, "bid_type": a.bid_type.value, "pctr": 0.05, "ad": a}
        for a in active_ads
    ]
    ranked = rank_ads_by_ecpm(ad_dicts)
    # 取排名靠前的广告，数量由频控决定
    selected = [r["ad"] for r in ranked[:freq_result["max_ads"]]]

    return {"ads": selected, "frequency_level": level, "remaining_today": freq_result["max_ads"]}


def record_impression(db: Session, user_id: int, ad_id: int, impression_type: str, context: Optional[dict]) -> None:
    """记录广告曝光或点击事件

    创建展示记录；若为CPC广告的点击事件，执行计费扣款，
    并在预算耗尽时将广告状态标记为已耗尽。

    Args:
        db: 数据库会话
        user_id: 用户ID
        ad_id: 广告ID
        impression_type: 事件类型（show/click/convert）
        context: 上下文信息
    """
    imp = AdImpression(
        ad_id=ad_id, user_id=user_id,
        impression_type=ImpressionType(impression_type),
        context=context,
    )
    db.add(imp)

    # 点击事件触发CPC计费逻辑
    if impression_type == "click":
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if ad and ad.bid_type.value == "CPC":
            # 计算点击扣费并累加已花费金额
            charge = calculate_cpc_charge(0.05, 0.0)
            ad.spent_amount += charge
            # 预算耗尽时自动停止投放
            if ad.spent_amount >= ad.total_budget:
                ad.status = AdStatus.exhausted

    db.commit()


def get_merchant_ads(db: Session, advertiser_id: int) -> list:
    """获取商家的所有广告列表

    Args:
        db: 数据库会话
        advertiser_id: 广告主ID

    Returns:
        list: 该广告主的所有广告对象列表
    """
    return db.query(Ad).filter(Ad.advertiser_id == advertiser_id).all()


def get_ad_stats(db: Session, ad_id: int) -> dict:
    """获取广告投放效果统计

    统计展示数、点击数、转化数，计算点击率和已消耗金额。

    Args:
        db: 数据库会话
        ad_id: 广告ID

    Returns:
        dict: 包含展示/点击/转化数、点击率、已花费金额
    """
    # 分别统计展示、点击、转化次数
    shows = db.query(AdImpression).filter(AdImpression.ad_id == ad_id, AdImpression.impression_type == ImpressionType.show).count()
    clicks = db.query(AdImpression).filter(AdImpression.ad_id == ad_id, AdImpression.impression_type == ImpressionType.click).count()
    converts = db.query(AdImpression).filter(AdImpression.ad_id == ad_id, AdImpression.impression_type == ImpressionType.convert).count()
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    # 计算点击率，展示数为0时点击率为0
    ctr = clicks / shows if shows > 0 else 0.0
    return {
        "ad_id": ad_id, "total_shows": shows, "total_clicks": clicks,
        "total_converts": converts, "ctr": round(ctr, 4),
        "spent": ad.spent_amount if ad else 0.0,
    }
