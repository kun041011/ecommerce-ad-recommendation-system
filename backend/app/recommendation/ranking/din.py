"""DIN深度兴趣网络排序模型模块

实现DIN（Deep Interest Network）模型，通过注意力机制动态捕获
用户对候选物品的兴趣强度，解决用户兴趣多样性问题。
支持PyTorch和Numpy两种后端。
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
    class AttentionLayer(nn.Module):
        """注意力层

        计算候选物品与用户历史行为序列中每个物品的注意力权重，
        输入特征包括查询、键、差值和逐元素乘积四部分。
        """
        def __init__(self, embed_dim: int):
            super().__init__()
            # 注意力网络：4倍嵌入维度输入 -> 64 -> 1
            self.attn = nn.Sequential(
                nn.Linear(embed_dim * 4, 64),
                nn.ReLU(),
                nn.Linear(64, 1),
            )

        def forward(self, queries, keys, mask):
            """计算注意力加权的用户兴趣表示

            参数:
                queries: 候选物品嵌入，形状(batch, 1, dim)
                keys: 行为序列嵌入，形状(batch, seq_len, dim)
                mask: 有效位置掩码，形状(batch, seq_len)

            返回:
                Tensor: 注意力加权后的用户兴趣向量，形状(batch, dim)
            """
            # 扩展查询向量与键向量对齐
            queries = queries.expand_as(keys)
            # 拼接四组特征：查询、键、差值、逐元素乘积
            attn_input = torch.cat([queries, keys, queries - keys, queries * keys], dim=-1)
            attn_scores = self.attn(attn_input).squeeze(-1)
            # 对无效位置填充负无穷，softmax后权重趋近于0
            attn_scores = attn_scores.masked_fill(~mask, float("-inf"))
            attn_weights = torch.softmax(attn_scores, dim=-1)
            attn_weights = attn_weights.unsqueeze(1)
            # 加权求和得到用户兴趣表示
            return torch.bmm(attn_weights, keys).squeeze(1)

    class DIN(nn.Module):
        """DIN深度兴趣网络（PyTorch版本）

        通过注意力机制为不同候选物品激活用户历史行为中的相关兴趣，
        实现用户兴趣的动态表达。
        """
        def __init__(self, num_products: int, embed_dim: int, hidden_dims: List[int], max_seq_len: int):
            """初始化DIN模型

            参数:
                num_products: 商品总数
                embed_dim: 嵌入向量维度
                hidden_dims: DNN各隐藏层维度列表
                max_seq_len: 行为序列最大长度
            """
            super().__init__()
            self.product_embedding = nn.Embedding(num_products, embed_dim)  # 商品嵌入层
            self.attention = AttentionLayer(embed_dim)                       # 注意力层
            self.max_seq_len = max_seq_len

            # DNN部分：兴趣向量 + 候选嵌入 -> 多层全连接
            dnn_input = embed_dim * 2
            layers = []  # type: list
            in_dim = dnn_input
            for h in hidden_dims:
                layers.extend([nn.Linear(in_dim, h), nn.ReLU(), nn.Dropout(0.2)])
                in_dim = h
            layers.append(nn.Linear(in_dim, 1))
            self.dnn = nn.Sequential(*layers)
            self.output = nn.Sigmoid()

        def forward(self, behavior_seq, seq_lengths, candidate):
            """前向传播

            参数:
                behavior_seq: 用户行为序列，形状(batch, max_seq_len)
                seq_lengths: 各样本有效序列长度，形状(batch,)
                candidate: 候选商品ID，形状(batch,)

            返回:
                Tensor: 预测点击率，形状(batch, 1)
            """
            # 行为序列和候选商品的嵌入查表
            seq_embed = self.product_embedding(behavior_seq)
            cand_embed = self.product_embedding(candidate).unsqueeze(1)

            # 构建序列有效位置掩码
            mask = torch.arange(behavior_seq.size(1), device=behavior_seq.device).unsqueeze(0) < seq_lengths.unsqueeze(1)
            # 注意力机制提取用户兴趣
            user_interest = self.attention(cand_embed, seq_embed, mask)

            # 拼接兴趣向量和候选嵌入，经DNN预测点击率
            dnn_input = torch.cat([user_interest, cand_embed.squeeze(1)], dim=1)
            return self.output(self.dnn(dnn_input))

else:
    class DIN:
        """DIN深度兴趣网络（Numpy模拟版本）

        在无PyTorch环境下提供相同接口的Numpy实现，
        使用简化的注意力计算进行推理。
        """

        def __init__(self, num_products: int, embed_dim: int, hidden_dims: List[int], max_seq_len: int):
            """初始化DIN模型

            参数:
                num_products: 商品总数
                embed_dim: 嵌入向量维度
                hidden_dims: DNN各隐藏层维度列表
                max_seq_len: 行为序列最大长度
            """
            self.num_products = num_products
            self.embed_dim = embed_dim
            self.max_seq_len = max_seq_len
            rng = np.random.RandomState(42)
            # 随机初始化商品嵌入矩阵
            self.product_embedding = rng.randn(num_products, embed_dim).astype(np.float32) * 0.01
            # 初始化DNN各层权重和偏置
            dims = [embed_dim * 2] + hidden_dims + [1]
            self.weights = []
            self.biases = []
            for i in range(len(dims) - 1):
                self.weights.append(rng.randn(dims[i], dims[i + 1]).astype(np.float32) * 0.01)
                self.biases.append(np.zeros(dims[i + 1], dtype=np.float32))

        def predict(self, behavior_seq: np.ndarray, seq_lengths: np.ndarray, candidate: np.ndarray) -> np.ndarray:
            """预测点击率

            参数:
                behavior_seq: 用户行为序列，形状(batch, max_seq_len)
                seq_lengths: 各样本有效序列长度，形状(batch,)
                candidate: 候选商品ID，形状(batch,)

            返回:
                ndarray: 预测点击率，形状(batch, 1)
            """
            batch = behavior_seq.shape[0]
            # 行为序列和候选商品的嵌入查表
            seq_embed = self.product_embedding[behavior_seq]    # (batch, seq, dim)
            cand_embed = self.product_embedding[candidate]       # (batch, dim)

            # 简化注意力：候选商品与行为序列的点积相似度
            cand_exp = cand_embed[:, np.newaxis, :]  # (batch, 1, dim)
            scores = (seq_embed * cand_exp).sum(axis=2)  # (batch, seq)
            # 构建序列有效位置掩码
            mask = np.arange(behavior_seq.shape[1])[np.newaxis, :] < seq_lengths[:, np.newaxis]
            # 对无效位置填充极小值
            scores = np.where(mask, scores, -1e9)
            # Softmax计算注意力权重
            exp_scores = np.exp(scores - scores.max(axis=1, keepdims=True))
            exp_scores = np.where(mask, exp_scores, 0)
            attn_weights = exp_scores / (exp_scores.sum(axis=1, keepdims=True) + 1e-8)
            # 加权求和得到用户兴趣表示
            user_interest = (attn_weights[:, :, np.newaxis] * seq_embed).sum(axis=1)  # (batch, dim)

            # 拼接兴趣向量和候选嵌入，逐层DNN前向传播
            x = np.concatenate([user_interest, cand_embed], axis=1)
            for w, b in zip(self.weights[:-1], self.biases[:-1]):
                x = np.maximum(0, x @ w + b)  # ReLU激活
            x = x @ self.weights[-1] + self.biases[-1]
            # Sigmoid输出预测概率
            return 1.0 / (1.0 + np.exp(-x))
