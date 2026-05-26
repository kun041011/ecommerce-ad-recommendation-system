"""广告竞价排序模块

将不同出价类型（CPM/CPC）的广告统一转换为eCPM进行排序，
实现公平的竞价比较机制。
"""

from typing import List


def compute_ecpm(ad: dict) -> float:
    """计算广告的eCPM（等效千次展示成本）

    CPM广告直接使用出价金额；CPC广告通过 出价*预估点击率*1000 换算。

    Args:
        ad: 广告字典，包含 bid_type、bid_amount、pctr 等字段

    Returns:
        float: 等效eCPM值
    """
    if ad["bid_type"] == "CPM":
        # CPM出价类型，eCPM即为出价金额
        return ad["bid_amount"]
    # CPC出价类型，通过预估点击率换算为eCPM
    return ad["bid_amount"] * ad.get("pctr", 0.01) * 1000


def rank_ads_by_ecpm(ads: List[dict]) -> List[dict]:
    """按eCPM降序排列广告列表

    为每个广告计算eCPM并写入字典，然后按eCPM从高到低排序。

    Args:
        ads: 广告字典列表

    Returns:
        List[dict]: 按eCPM降序排列的广告列表
    """
    # 为每个广告计算并存储eCPM值
    for ad in ads:
        ad["ecpm"] = compute_ecpm(ad)
    # 按eCPM降序排序，eCPM越高排名越靠前
    return sorted(ads, key=lambda a: a["ecpm"], reverse=True)
