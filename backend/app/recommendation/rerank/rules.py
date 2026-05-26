"""业务规则过滤模块

在推荐结果返回用户前，应用业务规则进行最终过滤，
移除用户已购买和已展示的商品，保证推荐结果的有效性。
"""

from typing import List, Set


def apply_business_rules(
    items: List[dict],
    purchased_ids: Set[int],
    shown_ids: Set[int],
) -> List[dict]:
    """应用业务规则过滤推荐候选

    过滤掉用户已购买和已展示的商品，避免重复推荐。

    参数:
        items: 推荐候选物品列表，每个物品需包含 id 字段
        purchased_ids: 用户已购买的商品ID集合
        shown_ids: 用户已展示过的商品ID集合

    返回:
        List[dict]: 过滤后的物品列表
    """
    # 排除已购买和已展示的商品
    return [
        item for item in items
        if item["id"] not in purchased_ids and item["id"] not in shown_ids
    ]
