import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Optional


class ContentBasedRecall:
    def __init__(self):
        self.tfidf_matrix = None
        self.sim_matrix = None

    def fit(self, product_texts: List[str]):
        try:
            vectorizer = TfidfVectorizer()
            self.tfidf_matrix = vectorizer.fit_transform(product_texts)
            self.sim_matrix = cosine_similarity(self.tfidf_matrix)
            np.fill_diagonal(self.sim_matrix, 0)
        except ValueError:
            self.sim_matrix = None

    def recommend(self, liked_indices: List[int], n: int = 10, exclude_indices: Optional[List[int]] = None) -> List[int]:
        if self.sim_matrix is None or not liked_indices:
            return []

        scores = np.mean(self.sim_matrix[liked_indices], axis=0)
        if exclude_indices:
            for idx in exclude_indices:
                scores[idx] = -1

        top_indices = np.argsort(scores)[::-1][:n]
        return [int(i) for i in top_indices if scores[i] > 0]
