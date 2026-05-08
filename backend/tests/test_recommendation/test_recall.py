import numpy as np
from app.recommendation.recall.content_based import ContentBasedRecall
from app.recommendation.recall.als import ALSRecall
from app.recommendation.recall.hot import HotRecall


def test_content_based():
    product_tags = [
        "laptop computer gaming",
        "phone mobile smartphone",
        "laptop ultrabook portable",
        "headphones audio music",
    ]
    cb = ContentBasedRecall()
    cb.fit(product_tags)
    recs = cb.recommend(liked_indices=[0], n=2, exclude_indices=[0])
    assert 2 in recs


def test_content_based_empty():
    cb = ContentBasedRecall()
    cb.fit(["a", "b"])
    recs = cb.recommend(liked_indices=[], n=2)
    assert recs == []


def test_als_recall():
    matrix = np.array([
        [5, 3, 0, 1],
        [4, 0, 0, 1],
        [1, 1, 0, 5],
        [0, 0, 5, 4],
    ], dtype=float)
    als = ALSRecall(n_components=2)
    als.fit(matrix)
    recs = als.recommend(user_idx=1, n=2, exclude_interacted=True)
    assert len(recs) <= 2


def test_hot_recall():
    hot = HotRecall()
    hot.update({10: 500, 20: 300, 30: 100, 40: 800})
    recs = hot.recommend(n=2)
    assert recs[0] == 40
    assert recs[1] == 10
