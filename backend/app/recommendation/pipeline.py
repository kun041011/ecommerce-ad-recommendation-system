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
    def __init__(self):
        self.user_cf = UserCF()
        self.item_cf = ItemCF()
        self.content_based = ContentBasedRecall()
        self.hot = HotRecall()
        self._fitted = False

    def fit(self, interaction_matrix: np.ndarray, product_texts: List[str], product_views: dict):
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
        product_ids = product_ids or []
        purchased_ids = purchased_ids or set()

        if not self._fitted or user_idx is None:
            hot_recs = self.hot.recommend(n=n * 2, exclude_ids=purchased_ids)
            if hot_recs:
                return hot_recs[:n]
            candidates = [pid for pid in product_ids if pid not in purchased_ids]
            random.shuffle(candidates)
            return candidates[:n]

        candidates = set()
        for recall_fn in [
            lambda: self.user_cf.recommend(user_idx, n=n * 3),
            lambda: self.item_cf.recommend(user_idx, n=n * 3),
        ]:
            candidates.update(recall_fn())

        candidate_items = [
            {"id": pid, "score": 1.0 / (rank + 1), "category": "default"}
            for rank, pid in enumerate(candidates)
            if pid < len(product_ids)
        ]

        filtered = apply_business_rules(candidate_items, purchased_ids, set())
        reranked = mmr_rerank(filtered, n=n)
        result = [item["id"] for item in reranked]

        if len(result) < n:
            hot_fill = self.hot.recommend(n=n - len(result), exclude_ids=set(result) | purchased_ids)
            result.extend(hot_fill)

        return result[:n]
