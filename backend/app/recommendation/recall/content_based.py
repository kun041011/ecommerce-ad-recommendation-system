"""基于内容的推荐召回模块

利用TF-IDF提取商品文本特征，计算商品间内容相似度，
根据用户历史喜好物品推荐内容相似的其他商品。
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Optional


class ContentBasedRecall:
    """基于内容的推荐召回器

    核心思路：通过TF-IDF向量化商品文本描述，
    计算商品间的内容相似度，推荐与用户偏好内容相似的商品。
    """

    def __init__(self):
        self.tfidf_matrix = None   # TF-IDF特征矩阵
        self.sim_matrix = None     # 商品内容相似度矩阵

    def fit(self, product_texts: List[str]):
        """训练模型，构建商品内容相似度矩阵

        参数:
            product_texts: 商品文本描述列表（标题、描述等拼接文本）
        """
        try:
            # 使用TF-IDF对商品文本进行向量化
            vectorizer = TfidfVectorizer()
            self.tfidf_matrix = vectorizer.fit_transform(product_texts)
            # 计算商品间的余弦相似度
            self.sim_matrix = cosine_similarity(self.tfidf_matrix)
            # 对角线置零，排除商品与自身的相似度
            np.fill_diagonal(self.sim_matrix, 0)
        except ValueError:
            # 文本为空或无有效词汇时，置空处理
            self.sim_matrix = None

    def recommend(self, liked_indices: List[int], n: int = 10, exclude_indices: Optional[List[int]] = None) -> List[int]:
        """根据用户喜好商品推荐相似内容的商品

        对用户喜欢的商品集合，取平均相似度作为推荐分数。

        参数:
            liked_indices: 用户喜好的商品索引列表
            n: 推荐数量
            exclude_indices: 需要排除的商品索引列表

        返回:
            List[int]: 推荐商品索引列表
        """
        if self.sim_matrix is None or not liked_indices:
            return []

        # 对用户喜欢的多个商品取平均相似度
        scores = np.mean(self.sim_matrix[liked_indices], axis=0)
        # 排除指定商品
        if exclude_indices:
            for idx in exclude_indices:
                scores[idx] = -1

        # 按分数降序取Top-N
        top_indices = np.argsort(scores)[::-1][:n]
        return [int(i) for i in top_indices if scores[i] > 0]
