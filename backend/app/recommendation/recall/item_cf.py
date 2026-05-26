"""基于物品的协同过滤召回模块

通过计算物品之间的余弦相似度，找到与用户已交互物品相似的其他物品，
作为推荐候选集的一路召回来源。
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List


class ItemCF:
    """基于物品的协同过滤推荐器

    核心思路：与用户喜欢的物品相似的物品，用户也可能喜欢。
    使用物品-用户交互矩阵（转置）计算物品间余弦相似度。
    """

    def __init__(self):
        self.item_sim_matrix = None      # 物品相似度矩阵
        self.interaction_matrix = None   # 用户-物品交互矩阵

    def fit(self, interaction_matrix: np.ndarray):
        """训练模型，计算物品相似度矩阵

        参数:
            interaction_matrix: 用户-物品交互矩阵，行为用户，列为物品
        """
        self.interaction_matrix = interaction_matrix
        # 转置后计算物品间的余弦相似度
        self.item_sim_matrix = cosine_similarity(interaction_matrix.T)
        # 对角线置零，排除物品与自身的相似度
        np.fill_diagonal(self.item_sim_matrix, 0)

    def recommend(self, user_idx: int, n: int = 10, exclude_interacted: bool = True) -> List[int]:
        """为指定用户生成推荐物品列表

        根据用户已交互的物品，利用物品相似度加权求和计算推荐分数。

        参数:
            user_idx: 目标用户索引
            n: 推荐物品数量
            exclude_interacted: 是否排除用户已交互的物品

        返回:
            List[int]: 推荐物品索引列表
        """
        if self.item_sim_matrix is None:
            return []

        # 获取用户的交互评分向量
        user_ratings = self.interaction_matrix[user_idx]
        # 加权求和：用户评分 × 物品相似度矩阵
        scores = user_ratings @ self.item_sim_matrix

        # 排除用户已交互的物品
        if exclude_interacted:
            interacted = user_ratings > 0
            scores[interacted] = -1

        # 按分数降序取Top-N
        top_indices = np.argsort(scores)[::-1][:n]
        return [int(i) for i in top_indices if scores[i] > 0]
