from typing import Optional

from sqlalchemy.orm import Session

from app.activity.scorer import calculate_activity_score, classify_activity_level
from app.ad_engine.bidding import rank_ads_by_ecpm
from app.ad_engine.billing import calculate_cpc_charge
from app.ad_engine.frequency import FrequencyController
from app.models.ad import Ad, AdImpression, AdStatus, ImpressionType
from app.models.behavior import UserBehavior
from app.models.user import User

freq_controller = FrequencyController()


def create_ad(db: Session, advertiser_id: int, **kwargs) -> Ad:
    ad = Ad(advertiser_id=advertiser_id, **kwargs)
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad


def fetch_ads_for_user(db: Session, user: User) -> dict:
    behaviors = db.query(UserBehavior).filter(UserBehavior.user_id == user.id).all()
    behavior_dicts = [{"behavior_type": b.behavior_type.value, "created_at": b.created_at} for b in behaviors]
    score = calculate_activity_score(behavior_dicts)
    level = classify_activity_level(score)

    today_count = db.query(AdImpression).filter(
        AdImpression.user_id == user.id,
        AdImpression.impression_type == ImpressionType.show,
    ).count()

    last_impression = db.query(AdImpression).filter(
        AdImpression.user_id == user.id,
        AdImpression.impression_type == ImpressionType.show,
    ).order_by(AdImpression.created_at.desc()).first()
    last_ts = last_impression.created_at.timestamp() if last_impression else 0

    freq_result = freq_controller.check(user.id, level, today_count, last_ts)
    if not freq_result["allowed"]:
        return {"ads": [], "frequency_level": level, "remaining_today": 0}

    active_ads = db.query(Ad).filter(Ad.status == AdStatus.active).all()
    ad_dicts = [
        {"id": a.id, "bid_amount": a.bid_amount, "bid_type": a.bid_type.value, "pctr": 0.05, "ad": a}
        for a in active_ads
    ]
    ranked = rank_ads_by_ecpm(ad_dicts)
    selected = [r["ad"] for r in ranked[:freq_result["max_ads"]]]

    return {"ads": selected, "frequency_level": level, "remaining_today": freq_result["max_ads"]}


def record_impression(db: Session, user_id: int, ad_id: int, impression_type: str, context: Optional[dict]) -> None:
    imp = AdImpression(
        ad_id=ad_id, user_id=user_id,
        impression_type=ImpressionType(impression_type),
        context=context,
    )
    db.add(imp)

    if impression_type == "click":
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if ad and ad.bid_type.value == "CPC":
            charge = calculate_cpc_charge(0.05, 0.0)
            ad.spent_amount += charge
            if ad.spent_amount >= ad.total_budget:
                ad.status = AdStatus.exhausted

    db.commit()


def get_merchant_ads(db: Session, advertiser_id: int) -> list:
    return db.query(Ad).filter(Ad.advertiser_id == advertiser_id).all()


def get_ad_stats(db: Session, ad_id: int) -> dict:
    shows = db.query(AdImpression).filter(AdImpression.ad_id == ad_id, AdImpression.impression_type == ImpressionType.show).count()
    clicks = db.query(AdImpression).filter(AdImpression.ad_id == ad_id, AdImpression.impression_type == ImpressionType.click).count()
    converts = db.query(AdImpression).filter(AdImpression.ad_id == ad_id, AdImpression.impression_type == ImpressionType.convert).count()
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    ctr = clicks / shows if shows > 0 else 0.0
    return {
        "ad_id": ad_id, "total_shows": shows, "total_clicks": clicks,
        "total_converts": converts, "ctr": round(ctr, 4),
        "spent": ad.spent_amount if ad else 0.0,
    }
