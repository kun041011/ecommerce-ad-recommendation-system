import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Optional


class UserCF:
    def __init__(self):
        self.user_sim_matrix = None
        self.interaction_matrix = None

    def fit(self, interaction_matrix: np.ndarray):
        self.interaction_matrix = interaction_matrix
        self.user_sim_matrix = cosine_similarity(interaction_matrix)
        np.fill_diagonal(self.user_sim_matrix, 0)

    def recommend(self, user_idx: int, n: int = 10, exclude_interacted: bool = True) -> List[int]:
        if self.user_sim_matrix is None:
            return []

        sim_scores = self.user_sim_matrix[user_idx]
        weighted_scores = sim_scores @ self.interaction_matrix

        if exclude_interacted:
            interacted = self.interaction_matrix[user_idx] > 0
            weighted_scores[interacted] = -1

        top_indices = np.argsort(weighted_scores)[::-1][:n]
        return [int(i) for i in top_indices if weighted_scores[i] > 0]
