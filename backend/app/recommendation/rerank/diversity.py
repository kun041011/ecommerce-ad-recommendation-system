"""MMR多样性重排模块

实现最大边际相关性（Maximal Marginal Relevance）算法，
在保持推荐相关性的同时提升结果多样性，避免同类商品扎堆。
"""

from typing import List, Dict


def mmr_rerank(items: List[dict], n: int = 10, lambda_param: float = 0.5) -> List[dict]:
    """使用MMR算法对推荐结果进行多样性重排

    MMR公式：score = lambda * relevance - (1-lambda) * max_similarity
    lambda越大越偏重相关性，越小越偏重多样性。

    参数:
        items: 候选物品列表，每个物品需包含 score 和 category 字段
        n: 重排后返回的物品数量
        lambda_param: 相关性与多样性的权衡参数（0-1），默认0.5

    返回:
        List[dict]: 重排后的物品列表
    """
    if not items:
        return []

    # 贪心选择：首先选取相关性最高的物品
    selected = [items[0]]
    remaining = items[1:]

    # 迭代选择：每次选取MMR分数最高的物品
    while len(selected) < n and remaining:
        best_score = -float("inf")
        best_idx = 0

        for i, item in enumerate(remaining):
            # 相关性分数
            relevance = item.get("score", 0)
            # 与已选物品集合的最大相似度（基于类别是否相同）
            max_sim = max(
                (1.0 if item.get("category") == s.get("category") else 0.0)
                for s in selected
            )
            # MMR分数 = 相关性加权 - 相似度惩罚
            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = i

        # 将最优候选加入已选集合
        selected.append(remaining.pop(best_idx))

    return selected
