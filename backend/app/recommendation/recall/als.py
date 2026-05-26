"""ALS矩阵分解召回模块

使用非负矩阵分解（NMF）将用户-物品交互矩阵分解为
用户隐因子和物品隐因子，通过隐因子内积预测用户偏好。
"""

import numpy as np
from sklearn.decomposition import NMF
from typing import List


class ALSRecall:
    """ALS矩阵分解推荐器

    核心思路：将高维稀疏的交互矩阵分解为低维稠密的用户因子和物品因子，
    通过因子向量的内积预测用户对未交互物品的偏好分数。
    """

    def __init__(self, n_components: int = 10):
        """初始化ALS推荐器

        Args:
            n_components: 隐因子维度数，控制模型的表达能力
        """
        self.n_components = n_components
        self.user_factors = None       # 用户隐因子矩阵
        self.item_factors = None       # 物品隐因子矩阵
        self.interaction_matrix = None # 原始交互矩阵

    def fit(self, interaction_matrix: np.ndarray):
        """训练模型，分解用户-物品交互矩阵

        使用NMF将交互矩阵分解为 用户因子(U) × 物品因子(V^T)。

        Args:
            interaction_matrix: 用户-物品交互矩阵
        """
        self.interaction_matrix = interaction_matrix
        # 隐因子维度不超过矩阵的最小维度
        n_components = min(self.n_components, min(interaction_matrix.shape))
        model = NMF(n_components=n_components, init="random", random_state=42, max_iter=200)
        # 分解得到用户因子和物品因子
        self.user_factors = model.fit_transform(interaction_matrix)
        self.item_factors = model.components_.T  # 转置为(物品数, 隐因子维度)

    def recommend(self, user_idx: int, n: int = 10, exclude_interacted: bool = True) -> List[int]:
        """为指定用户生成推荐物品列表

        通过用户因子与物品因子的内积计算偏好分数。

        Args:
            user_idx: 目标用户索引
            n: 推荐物品数量
            exclude_interacted: 是否排除用户已交互的物品

        Returns:
            List[int]: 推荐物品索引列表
        """
        if self.user_factors is None:
            return []

        # 用户隐因子与所有物品隐因子做内积，得到预测分数
        scores = self.user_factors[user_idx] @ self.item_factors.T

        # 排除用户已交互的物品
        if exclude_interacted:
            interacted = self.interaction_matrix[user_idx] > 0
            scores[interacted] = -1

        # 按分数降序取Top-N
        top_indices = np.argsort(scores)[::-1][:n]
        return [int(i) for i in top_indices if scores[i] > 0]
