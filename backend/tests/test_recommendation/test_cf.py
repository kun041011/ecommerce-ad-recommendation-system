import numpy as np
from app.recommendation.recall.user_cf import UserCF
from app.recommendation.recall.item_cf import ItemCF


def test_user_cf_fit_and_recommend():
    interaction_matrix = np.array([
        [5, 3, 0, 1],
        [4, 0, 0, 1],
        [1, 1, 0, 5],
        [0, 0, 5, 4],
    ], dtype=float)

    ucf = UserCF()
    ucf.fit(interaction_matrix)
    recs = ucf.recommend(user_idx=1, n=2, exclude_interacted=True)
    assert len(recs) <= 2
    assert all(isinstance(r, int) for r in recs)


def test_user_cf_empty_history():
    matrix = np.array([[0, 0, 0], [1, 0, 1]], dtype=float)
    ucf = UserCF()
    ucf.fit(matrix)
    recs = ucf.recommend(user_idx=0, n=2, exclude_interacted=True)
    assert isinstance(recs, list)


def test_item_cf_fit_and_recommend():
    interaction_matrix = np.array([
        [5, 3, 0, 1],
        [4, 0, 0, 1],
        [1, 1, 0, 5],
        [0, 0, 5, 4],
    ], dtype=float)

    icf = ItemCF()
    icf.fit(interaction_matrix)
    recs = icf.recommend(user_idx=0, n=2, exclude_interacted=True)
    assert len(recs) <= 2
    assert 2 in recs
