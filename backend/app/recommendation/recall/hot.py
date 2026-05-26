"""热门召回模块

基于商品热度分数进行召回，适用于冷启动场景（新用户或无交互数据），
作为协同过滤和内容推荐的兜底补充策略。
"""

from typing import List, Dict, Optional, Set


class HotRecall:
    """热门商品召回器

    核心思路：按全局热度分数降序推荐商品，
    用于冷启动用户或其他召回通道候选不足时的补充。
    """

    def __init__(self):
        self.product_scores = {}  # type: Dict[int, float]  # 商品ID到热度分数的映射

    def update(self, scores: Dict[int, float]):
        """更新商品热度分数

        参数:
            scores: 商品ID到热度分数的映射字典
        """
        self.product_scores = scores

    def recommend(self, n: int = 10, exclude_ids: Optional[Set[int]] = None) -> List[int]:
        """推荐热门商品

        按热度分数降序排列，排除指定的商品ID。

        参数:
            n: 推荐数量
            exclude_ids: 需要排除的商品ID集合

        返回:
            List[int]: 热门商品ID列表
        """
        exclude = exclude_ids or set()
        # 过滤已排除的商品，按热度分数降序排序
        sorted_items = sorted(
            ((pid, score) for pid, score in self.product_scores.items() if pid not in exclude),
            key=lambda x: x[1],
            reverse=True,
        )
        # 取前N个商品ID
        return [pid for pid, _ in sorted_items[:n]]
