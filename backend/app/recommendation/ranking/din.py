"""DIN (Deep Interest Network) ranking model.

Uses PyTorch when available, falls back to a numpy simulation.
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
        def __init__(self, embed_dim: int):
            super().__init__()
            self.attn = nn.Sequential(
                nn.Linear(embed_dim * 4, 64),
                nn.ReLU(),
                nn.Linear(64, 1),
            )

        def forward(self, queries, keys, mask):
            queries = queries.expand_as(keys)
            attn_input = torch.cat([queries, keys, queries - keys, queries * keys], dim=-1)
            attn_scores = self.attn(attn_input).squeeze(-1)
            attn_scores = attn_scores.masked_fill(~mask, float("-inf"))
            attn_weights = torch.softmax(attn_scores, dim=-1)
            attn_weights = attn_weights.unsqueeze(1)
            return torch.bmm(attn_weights, keys).squeeze(1)

    class DIN(nn.Module):
        def __init__(self, num_products: int, embed_dim: int, hidden_dims: List[int], max_seq_len: int):
            super().__init__()
            self.product_embedding = nn.Embedding(num_products, embed_dim)
            self.attention = AttentionLayer(embed_dim)
            self.max_seq_len = max_seq_len

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
            seq_embed = self.product_embedding(behavior_seq)
            cand_embed = self.product_embedding(candidate).unsqueeze(1)

            mask = torch.arange(behavior_seq.size(1), device=behavior_seq.device).unsqueeze(0) < seq_lengths.unsqueeze(1)
            user_interest = self.attention(cand_embed, seq_embed, mask)

            dnn_input = torch.cat([user_interest, cand_embed.squeeze(1)], dim=1)
            return self.output(self.dnn(dnn_input))

else:
    class DIN:
        """Numpy-based DIN simulation for environments without PyTorch."""

        def __init__(self, num_products: int, embed_dim: int, hidden_dims: List[int], max_seq_len: int):
            self.num_products = num_products
            self.embed_dim = embed_dim
            self.max_seq_len = max_seq_len
            rng = np.random.RandomState(42)
            self.product_embedding = rng.randn(num_products, embed_dim).astype(np.float32) * 0.01
            dims = [embed_dim * 2] + hidden_dims + [1]
            self.weights = []
            self.biases = []
            for i in range(len(dims) - 1):
                self.weights.append(rng.randn(dims[i], dims[i + 1]).astype(np.float32) * 0.01)
                self.biases.append(np.zeros(dims[i + 1], dtype=np.float32))

        def predict(self, behavior_seq: np.ndarray, seq_lengths: np.ndarray, candidate: np.ndarray) -> np.ndarray:
            batch = behavior_seq.shape[0]
            seq_embed = self.product_embedding[behavior_seq]    # (batch, seq, dim)
            cand_embed = self.product_embedding[candidate]       # (batch, dim)

            # Simple attention: weighted average of sequence by similarity to candidate
            cand_exp = cand_embed[:, np.newaxis, :]  # (batch, 1, dim)
            scores = (seq_embed * cand_exp).sum(axis=2)  # (batch, seq)
            mask = np.arange(behavior_seq.shape[1])[np.newaxis, :] < seq_lengths[:, np.newaxis]
            scores = np.where(mask, scores, -1e9)
            exp_scores = np.exp(scores - scores.max(axis=1, keepdims=True))
            exp_scores = np.where(mask, exp_scores, 0)
            attn_weights = exp_scores / (exp_scores.sum(axis=1, keepdims=True) + 1e-8)
            user_interest = (attn_weights[:, :, np.newaxis] * seq_embed).sum(axis=1)  # (batch, dim)

            x = np.concatenate([user_interest, cand_embed], axis=1)
            for w, b in zip(self.weights[:-1], self.biases[:-1]):
                x = np.maximum(0, x @ w + b)
            x = x @ self.weights[-1] + self.biases[-1]
            return 1.0 / (1.0 + np.exp(-x))
