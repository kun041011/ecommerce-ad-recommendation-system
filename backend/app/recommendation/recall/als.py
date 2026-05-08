import numpy as np
from sklearn.decomposition import NMF
from typing import List


class ALSRecall:
    def __init__(self, n_components: int = 10):
        self.n_components = n_components
        self.user_factors = None
        self.item_factors = None
        self.interaction_matrix = None

    def fit(self, interaction_matrix: np.ndarray):
        self.interaction_matrix = interaction_matrix
        n_components = min(self.n_components, min(interaction_matrix.shape))
        model = NMF(n_components=n_components, init="random", random_state=42, max_iter=200)
        self.user_factors = model.fit_transform(interaction_matrix)
        self.item_factors = model.components_.T

    def recommend(self, user_idx: int, n: int = 10, exclude_interacted: bool = True) -> List[int]:
        if self.user_factors is None:
            return []

        scores = self.user_factors[user_idx] @ self.item_factors.T

        if exclude_interacted:
            interacted = self.interaction_matrix[user_idx] > 0
            scores[interacted] = -1

        top_indices = np.argsort(scores)[::-1][:n]
        return [int(i) for i in top_indices if scores[i] > 0]
