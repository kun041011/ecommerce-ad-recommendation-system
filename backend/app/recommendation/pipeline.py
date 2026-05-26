"""推荐流水线模块

整合召回、排序和重排三个阶段，构建完整的推荐流水线。
多路召回（UserCF、ItemCF、热门）-> 业务规则过滤 -> MMR多样性重排。
冷启动场景自动降级为热门推荐或随机推荐。
"""

import random
import numpy as np
from typing import Optional, List, Set

from app.recommendation.recall.content_based import ContentBasedRecall
from app.recommendation.recall.hot import HotRecall
from app.recommendation.recall.item_cf import ItemCF
from app.recommendation.recall.user_cf import UserCF
from app.recommendation.rerank.diversity import mmr_rerank
from app.recommendation.rerank.rules import apply_business_rules


class RecommendationPipeline:
    """推荐流水线

    整合多路召回、业务规则过滤和多样性重排，
    为用户生成最终的推荐结果列表。
    """

    def __init__(self):
        """初始化推荐流水线，创建各路召回器实例"""
        self.user_cf = UserCF()                    # 基于用户的协同过滤
        self.item_cf = ItemCF()                    # 基于物品的协同过滤
        self.content_based = ContentBasedRecall()  # 基于内容的推荐
        self.hot = HotRecall()                     # 热门召回
        self._fitted = False                       # 模型是否已训练

    def fit(self, interaction_matrix: np.ndarray, product_texts: List[str], product_views: dict):
        """训练所有召回模型

        参数:
            interaction_matrix: 用户-物品交互矩阵
            product_texts: 商品文本描述列表
            product_views: 商品热度分数字典
        """
        self.user_cf.fit(interaction_matrix)
        self.item_cf.fit(interaction_matrix)
        self.content_based.fit(product_texts)
        self.hot.update(product_views)
        self._fitted = True

    def recommend(
        self,
        user_idx: Optional[int],
        n: int = 10,
        product_ids: Optional[List[int]] = None,
        purchased_ids: Optional[Set[int]] = None,
    ) -> List[int]:
        """为用户生成推荐结果

        流程：多路召回 -> 业务规则过滤 -> MMR多样性重排 -> 热门补充。

        参数:
            user_idx: 用户索引（None表示冷启动用户）
            n: 推荐数量
            product_ids: 全部商品ID列表
            purchased_ids: 用户已购买的商品ID集合

        返回:
            List[int]: 推荐商品ID列表
        """
        product_ids = product_ids or []
        purchased_ids = purchased_ids or set()

        # 冷启动降级：模型未训练或用户索引为空时，使用热门或随机推荐
        if not self._fitted or user_idx is None:
            hot_recs = self.hot.recommend(n=n * 2, exclude_ids=purchased_ids)
            if hot_recs:
                return hot_recs[:n]
            # 热门召回也为空时，随机选取商品
            candidates = [pid for pid in product_ids if pid not in purchased_ids]
            random.shuffle(candidates)
            return candidates[:n]

        # 多路召回：合并UserCF和ItemCF的召回结果，去重
        candidates = set()
        for recall_fn in [
            lambda: self.user_cf.recommend(user_idx, n=n * 3),
            lambda: self.item_cf.recommend(user_idx, n=n * 3),
        ]:
            candidates.update(recall_fn())

        # 将召回结果转换为带分数的候选列表，分数按排名倒数递减
        candidate_items = [
            {"id": pid, "score": 1.0 / (rank + 1), "category": "default"}
            for rank, pid in enumerate(candidates)
            if pid < len(product_ids)
        ]

        # 业务规则过滤：移除已购买商品
        filtered = apply_business_rules(candidate_items, purchased_ids, set())
        # MMR多样性重排
        reranked = mmr_rerank(filtered, n=n)
        result = [item["id"] for item in reranked]

        # 候选不足时，用热门推荐补充
        if len(result) < n:
            hot_fill = self.hot.recommend(n=n - len(result), exclude_ids=set(result) | purchased_ids)
            result.extend(hot_fill)

        return result[:n]
