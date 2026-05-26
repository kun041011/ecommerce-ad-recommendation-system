"""DeepFM排序模型模块

实现DeepFM深度因子分解机模型，融合FM的二阶特征交叉和DNN的高阶特征学习能力，
用于推荐系统精排阶段的点击率预估。支持PyTorch和Numpy两种后端。
"""
from typing import List

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

import numpy as np


if HAS_TORCH:
    class FMLayer(nn.Module):
        """FM因子分解层

        实现二阶特征交叉，通过数学公式化简避免显式两两交叉计算，
        复杂度从O(n^2)降至O(n)。
        """
        def __init__(self, embed_dim: int, num_fields: int):
            super().__init__()
            self.num_fields = num_fields

        def forward(self, embeddings):
            """前向传播，计算FM二阶交叉项

            利用公式：0.5 * (sum(vi)^2 - sum(vi^2))

            参数:
                embeddings: 特征嵌入张量，形状(batch, fields, dim)

            返回:
                Tensor: FM交叉项输出，形状(batch, 1)
            """
            # 先求和再平方
            sum_square = embeddings.sum(dim=1).pow(2)
            # 先平方再求和
            square_sum = embeddings.pow(2).sum(dim=1)
            return 0.5 * (sum_square - square_sum).sum(dim=1, keepdim=True)

    class DeepFM(nn.Module):
        """DeepFM模型（PyTorch版本）

        由FM层和DNN层并行组成，FM捕获二阶特征交叉，DNN学习高阶特征组合，
        两者输出相加后经Sigmoid得到点击率预估值。
        """
        def __init__(self, sparse_field_dims: List[int], embed_dim: int, dense_dim: int, hidden_dims: List[int]):
            """初始化DeepFM模型

            参数:
                sparse_field_dims: 各离散特征的取值数量列表
                embed_dim: 嵌入向量维度
                dense_dim: 连续特征维度
                hidden_dims: DNN各隐藏层维度列表
            """
            super().__init__()
            # 为每个离散特征域创建嵌入层
            self.embeddings = nn.ModuleList([
                nn.Embedding(dim, embed_dim) for dim in sparse_field_dims
            ])
            num_fields = len(sparse_field_dims)
            self.fm = FMLayer(embed_dim, num_fields)

            # 构建DNN部分：嵌入拼接 + 连续特征 -> 多层全连接
            dnn_input_dim = num_fields * embed_dim + dense_dim
            layers = []  # type: list
            in_dim = dnn_input_dim
            for h_dim in hidden_dims:
                layers.extend([nn.Linear(in_dim, h_dim), nn.ReLU(), nn.Dropout(0.2)])
                in_dim = h_dim
            layers.append(nn.Linear(in_dim, 1))
            self.dnn = nn.Sequential(*layers)
            self.output_layer = nn.Sigmoid()

        def forward(self, sparse_input, dense_input):
            """前向传播

            参数:
                sparse_input: 离散特征索引，形状(batch, num_fields)
                dense_input: 连续特征值，形状(batch, dense_dim)

            返回:
                Tensor: 预测点击率，形状(batch, 1)
            """
            # 离散特征嵌入查表
            embed_list = [self.embeddings[i](sparse_input[:, i]) for i in range(sparse_input.shape[1])]
            embed_stack = torch.stack(embed_list, dim=1)

            # FM分支：二阶特征交叉
            fm_out = self.fm(embed_stack)
            # DNN分支：嵌入展平拼接连续特征
            embed_flat = embed_stack.view(embed_stack.size(0), -1)
            dnn_input = torch.cat([embed_flat, dense_input], dim=1)
            dnn_out = self.dnn(dnn_input)

            # FM与DNN输出相加，经Sigmoid输出预测概率
            return self.output_layer(fm_out + dnn_out)

else:
    class DeepFM:
        """DeepFM模型（Numpy模拟版本）

        在无PyTorch环境下提供相同接口的Numpy实现，
        用于轻量级推理或测试场景。
        """

        def __init__(self, sparse_field_dims: List[int], embed_dim: int, dense_dim: int, hidden_dims: List[int]):
            """初始化DeepFM模型

            参数:
                sparse_field_dims: 各离散特征的取值数量列表
                embed_dim: 嵌入向量维度
                dense_dim: 连续特征维度
                hidden_dims: DNN各隐藏层维度列表
            """
            self.sparse_field_dims = sparse_field_dims
            self.embed_dim = embed_dim
            self.dense_dim = dense_dim
            self.hidden_dims = hidden_dims
            self.num_fields = len(sparse_field_dims)
            rng = np.random.RandomState(42)
            # 随机初始化嵌入表
            self.embed_tables = [rng.randn(dim, embed_dim).astype(np.float32) for dim in sparse_field_dims]
            # 初始化DNN各层权重和偏置
            dims = [self.num_fields * embed_dim + dense_dim] + hidden_dims + [1]
            self.weights = []
            self.biases = []
            for i in range(len(dims) - 1):
                self.weights.append(rng.randn(dims[i], dims[i + 1]).astype(np.float32) * 0.01)
                self.biases.append(np.zeros(dims[i + 1], dtype=np.float32))

        def predict(self, sparse_input: np.ndarray, dense_input: np.ndarray) -> np.ndarray:
            """预测点击率

            参数:
                sparse_input: 离散特征索引，形状(batch, num_fields)
                dense_input: 连续特征值，形状(batch, dense_dim)

            返回:
                ndarray: 预测点击率，形状(batch, 1)
            """
            batch = sparse_input.shape[0]
            # 离散特征嵌入查表
            embeds = []
            for i in range(self.num_fields):
                embeds.append(self.embed_tables[i][sparse_input[:, i]])
            embed_stack = np.stack(embeds, axis=1)  # (batch, fields, dim)

            # FM部分：二阶特征交叉
            sum_sq = embed_stack.sum(axis=1) ** 2
            sq_sum = (embed_stack ** 2).sum(axis=1)
            fm_out = 0.5 * (sum_sq - sq_sum).sum(axis=1, keepdims=True)

            # DNN部分：嵌入展平拼接连续特征，逐层前向传播
            x = np.concatenate([embed_stack.reshape(batch, -1), dense_input], axis=1)
            for w, b in zip(self.weights[:-1], self.biases[:-1]):
                x = np.maximum(0, x @ w + b)  # ReLU激活
            x = x @ self.weights[-1] + self.biases[-1]

            # FM与DNN输出相加，经Sigmoid输出预测概率
            logit = fm_out + x
            return 1.0 / (1.0 + np.exp(-logit))  # Sigmoid激活函数
