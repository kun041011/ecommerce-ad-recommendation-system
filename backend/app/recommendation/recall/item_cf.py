import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List


class ItemCF:
    def __init__(self):
        self.item_sim_matrix = None
        self.interaction_matrix = None

    def fit(self, interaction_matrix: np.ndarray):
        self.interaction_matrix = interaction_matrix
        self.item_sim_matrix = cosine_similarity(interaction_matrix.T)
        np.fill_diagonal(self.item_sim_matrix, 0)

    def recommend(self, user_idx: int, n: int = 10, exclude_interacted: bool = True) -> List[int]:
        if self.item_sim_matrix is None:
            return []

        user_ratings = self.interaction_matrix[user_idx]
        scores = user_ratings @ self.item_sim_matrix

        if exclude_interacted:
            interacted = user_ratings > 0
            scores[interacted] = -1

        top_indices = np.argsort(scores)[::-1][:n]
        return [int(i) for i in top_indices if scores[i] > 0]
