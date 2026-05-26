"""特征工程模块

负责将原始用户和商品特征编码为模型可用的格式，
将离散特征转换为索引，连续特征直接传递。
"""

from typing import Dict, List


class FeatureEncoder:
    """特征编码器

    将离散特征（如类别、品牌）转换为嵌入索引，
    连续特征（如价格、评分）保持数值格式，供排序模型使用。
    """

    def __init__(self, sparse_dims: Dict[str, int], dense_count: int):
        """初始化特征编码器

        参数:
            sparse_dims: 各离散特征域的取值数量，如 {"category": 50, "brand": 200}
            dense_count: 连续特征的数量
        """
        self.sparse_fields = list(sparse_dims.keys())   # 离散特征域名称列表
        self.sparse_dims = sparse_dims                    # 各域的取值维度
        self.dense_count = dense_count                    # 连续特征数量

    def encode(self, sparse: Dict[str, int], dense: List[float]) -> dict:
        """编码单条样本的特征

        将离散特征按域顺序提取索引，连续特征直接传递。

        参数:
            sparse: 离散特征字典，如 {"category": 3, "brand": 15}
            dense: 连续特征值列表，如 [29.9, 4.5]

        返回:
            dict: 包含 sparse_indices（离散索引列表）和 dense_values（连续值列表）
        """
        # 按字段顺序提取离散特征索引
        sparse_indices = [sparse[field] for field in self.sparse_fields]
        return {
            "sparse_indices": sparse_indices,
            "dense_values": dense,
        }
