"""基于用户的协同过滤召回模块

通过计算用户之间的余弦相似度，找到相似用户喜欢的物品，
作为推荐候选集的一路召回来源。
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Optional


class UserCF:
    """基于用户的协同过滤推荐器

    核心思路：相似用户喜欢的物品，当前用户也可能喜欢。
    使用用户-物品交互矩阵计算用户间余弦相似度。
    """

    def __init__(self):
        self.user_sim_matrix = None      # 用户相似度矩阵
        self.interaction_matrix = None   # 用户-物品交互矩阵

    def fit(self, interaction_matrix: np.ndarray):
        """训练模型，计算用户相似度矩阵

        参数:
            interaction_matrix: 用户-物品交互矩阵，行为用户，列为物品
        """
        self.interaction_matrix = interaction_matrix
        # 计算用户间的余弦相似度
        self.user_sim_matrix = cosine_similarity(interaction_matrix)
        # 对角线置零，排除用户与自身的相似度
        np.fill_diagonal(self.user_sim_matrix, 0)

    def recommend(self, user_idx: int, n: int = 10, exclude_interacted: bool = True) -> List[int]:
        """为指定用户生成推荐物品列表

        通过相似用户的交互行为加权求和，计算每个物品的推荐分数。

        参数:
            user_idx: 目标用户索引
            n: 推荐物品数量
            exclude_interacted: 是否排除用户已交互的物品

        返回:
            List[int]: 推荐物品索引列表
        """
        if self.user_sim_matrix is None:
            return []

        # 获取目标用户与所有用户的相似度
        sim_scores = self.user_sim_matrix[user_idx]
        # 加权求和：相似度 × 交互矩阵，得到每个物品的推荐分数
        weighted_scores = sim_scores @ self.interaction_matrix

        # 排除用户已交互的物品
        if exclude_interacted:
            interacted = self.interaction_matrix[user_idx] > 0
            weighted_scores[interacted] = -1

        # 按分数降序取Top-N
        top_indices = np.argsort(weighted_scores)[::-1][:n]
        return [int(i) for i in top_indices if weighted_scores[i] > 0]
