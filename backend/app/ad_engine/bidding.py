from typing import List


def compute_ecpm(ad: dict) -> float:
    if ad["bid_type"] == "CPM":
        return ad["bid_amount"]
    return ad["bid_amount"] * ad.get("pctr", 0.01) * 1000


def rank_ads_by_ecpm(ads: List[dict]) -> List[dict]:
    for ad in ads:
        ad["ecpm"] = compute_ecpm(ad)
    return sorted(ads, key=lambda a: a["ecpm"], reverse=True)
