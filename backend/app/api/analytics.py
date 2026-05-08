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
    total_users = db.query(func.count(User.id)).scalar()
    total_products = db.query(func.count(Product.id)).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()
    total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0
    total_ad_revenue = db.query(func.sum(Ad.spent_amount)).scalar() or 0
    total_shows = db.query(func.count(AdImpression.id)).filter(AdImpression.impression_type == ImpressionType.show).scalar()
    total_clicks = db.query(func.count(AdImpression.id)).filter(AdImpression.impression_type == ImpressionType.click).scalar()
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
    low = db.query(func.count(User.id)).filter(User.activity_score < 20).scalar()
    normal = db.query(func.count(User.id)).filter(User.activity_score >= 20, User.activity_score < 60).scalar()
    high = db.query(func.count(User.id)).filter(User.activity_score >= 60).scalar()
    return {"low": low, "normal": normal, "high": high}


@router.get("/ad-performance")
def ad_performance(db: Session = Depends(get_db), _user: User = Depends(require_admin)):
    ads = db.query(Ad).all()
    result = []
    for ad in ads:
        shows = db.query(func.count(AdImpression.id)).filter(
            AdImpression.ad_id == ad.id, AdImpression.impression_type == ImpressionType.show
        ).scalar()
        clicks = db.query(func.count(AdImpression.id)).filter(
            AdImpression.ad_id == ad.id, AdImpression.impression_type == ImpressionType.click
        ).scalar()
        result.append({
            "ad_id": ad.id, "title": ad.title, "shows": shows, "clicks": clicks,
            "ctr": round(clicks / shows, 4) if shows > 0 else 0, "spent": ad.spent_amount,
        })
    return result
