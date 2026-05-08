from typing import List, Dict, Optional, Set


class HotRecall:
    def __init__(self):
        self.product_scores = {}  # type: Dict[int, float]

    def update(self, scores: Dict[int, float]):
        self.product_scores = scores

    def recommend(self, n: int = 10, exclude_ids: Optional[Set[int]] = None) -> List[int]:
        exclude = exclude_ids or set()
        sorted_items = sorted(
            ((pid, score) for pid, score in self.product_scores.items() if pid not in exclude),
            key=lambda x: x[1],
            reverse=True,
        )
        return [pid for pid, _ in sorted_items[:n]]
