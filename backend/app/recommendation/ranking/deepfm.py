"""DeepFM ranking model.

Uses PyTorch when available, falls back to a numpy simulation for environments
where torch cannot be installed.
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
        def __init__(self, embed_dim: int, num_fields: int):
            super().__init__()
            self.num_fields = num_fields

        def forward(self, embeddings):
            sum_square = embeddings.sum(dim=1).pow(2)
            square_sum = embeddings.pow(2).sum(dim=1)
            return 0.5 * (sum_square - square_sum).sum(dim=1, keepdim=True)

    class DeepFM(nn.Module):
        def __init__(self, sparse_field_dims: List[int], embed_dim: int, dense_dim: int, hidden_dims: List[int]):
            super().__init__()
            self.embeddings = nn.ModuleList([
                nn.Embedding(dim, embed_dim) for dim in sparse_field_dims
            ])
            num_fields = len(sparse_field_dims)
            self.fm = FMLayer(embed_dim, num_fields)

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
            embed_list = [self.embeddings[i](sparse_input[:, i]) for i in range(sparse_input.shape[1])]
            embed_stack = torch.stack(embed_list, dim=1)

            fm_out = self.fm(embed_stack)
            embed_flat = embed_stack.view(embed_stack.size(0), -1)
            dnn_input = torch.cat([embed_flat, dense_input], dim=1)
            dnn_out = self.dnn(dnn_input)

            return self.output_layer(fm_out + dnn_out)

else:
    class DeepFM:
        """Numpy-based DeepFM simulation for environments without PyTorch."""

        def __init__(self, sparse_field_dims: List[int], embed_dim: int, dense_dim: int, hidden_dims: List[int]):
            self.sparse_field_dims = sparse_field_dims
            self.embed_dim = embed_dim
            self.dense_dim = dense_dim
            self.hidden_dims = hidden_dims
            self.num_fields = len(sparse_field_dims)
            rng = np.random.RandomState(42)
            self.embed_tables = [rng.randn(dim, embed_dim).astype(np.float32) for dim in sparse_field_dims]
            dims = [self.num_fields * embed_dim + dense_dim] + hidden_dims + [1]
            self.weights = []
            self.biases = []
            for i in range(len(dims) - 1):
                self.weights.append(rng.randn(dims[i], dims[i + 1]).astype(np.float32) * 0.01)
                self.biases.append(np.zeros(dims[i + 1], dtype=np.float32))

        def predict(self, sparse_input: np.ndarray, dense_input: np.ndarray) -> np.ndarray:
            batch = sparse_input.shape[0]
            embeds = []
            for i in range(self.num_fields):
                embeds.append(self.embed_tables[i][sparse_input[:, i]])
            embed_stack = np.stack(embeds, axis=1)  # (batch, fields, dim)

            # FM part
            sum_sq = embed_stack.sum(axis=1) ** 2
            sq_sum = (embed_stack ** 2).sum(axis=1)
            fm_out = 0.5 * (sum_sq - sq_sum).sum(axis=1, keepdims=True)

            # DNN part
            x = np.concatenate([embed_stack.reshape(batch, -1), dense_input], axis=1)
            for w, b in zip(self.weights[:-1], self.biases[:-1]):
                x = np.maximum(0, x @ w + b)  # ReLU
            x = x @ self.weights[-1] + self.biases[-1]

            logit = fm_out + x
            return 1.0 / (1.0 + np.exp(-logit))  # sigmoid
