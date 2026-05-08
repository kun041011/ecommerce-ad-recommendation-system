from app.recommendation.rerank.diversity import mmr_rerank
from app.recommendation.rerank.rules import apply_business_rules


def test_mmr_basic():
    items = [
        {"id": 1, "score": 0.9, "category": "A"},
        {"id": 2, "score": 0.85, "category": "A"},
        {"id": 3, "score": 0.8, "category": "B"},
        {"id": 4, "score": 0.7, "category": "C"},
    ]
    result = mmr_rerank(items, n=3, lambda_param=0.5)
    assert len(result) == 3
    categories = [r["category"] for r in result]
    assert len(set(categories)) >= 2


def test_mmr_empty():
    assert mmr_rerank([], n=5) == []


def test_business_rules_filter_purchased():
    items = [{"id": 1}, {"id": 2}, {"id": 3}]
    purchased_ids = {2}
    result = apply_business_rules(items, purchased_ids=purchased_ids, shown_ids=set())
    assert len(result) == 2
    assert all(r["id"] != 2 for r in result)


def test_business_rules_filter_shown():
    items = [{"id": 1}, {"id": 2}, {"id": 3}]
    result = apply_business_rules(items, purchased_ids=set(), shown_ids={1, 3})
    assert len(result) == 1
    assert result[0]["id"] == 2
