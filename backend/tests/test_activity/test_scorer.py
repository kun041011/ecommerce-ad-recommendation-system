import math
from datetime import datetime, timezone

from app.activity.scorer import (
    BEHAVIOR_WEIGHTS, calculate_activity_score, classify_activity_level, time_decay,
)


def test_time_decay_today():
    assert time_decay(0) == 1.0


def test_time_decay_7_days():
    result = time_decay(7)
    assert abs(result - math.exp(-0.7)) < 0.001


def test_time_decay_30_days():
    result = time_decay(30)
    assert result < 0.1


def test_behavior_weights_exist():
    assert BEHAVIOR_WEIGHTS["login"] == 2
    assert BEHAVIOR_WEIGHTS["purchase"] == 10
    assert BEHAVIOR_WEIGHTS["review"] == 5


def test_calculate_score_empty():
    assert calculate_activity_score([]) == 0.0


def test_calculate_score_single_login_today():
    now = datetime.now(timezone.utc)
    behaviors = [{"behavior_type": "login", "created_at": now}]
    score = calculate_activity_score(behaviors)
    assert abs(score - 2.0) < 0.01


def test_calculate_score_capped_at_100():
    now = datetime.now(timezone.utc)
    behaviors = [{"behavior_type": "purchase", "created_at": now}] * 20
    score = calculate_activity_score(behaviors)
    assert score == 100.0


def test_classify_high():
    assert classify_activity_level(60.0) == "high"
    assert classify_activity_level(100.0) == "high"


def test_classify_normal():
    assert classify_activity_level(20.0) == "normal"
    assert classify_activity_level(59.9) == "normal"


def test_classify_low():
    assert classify_activity_level(0.0) == "low"
    assert classify_activity_level(19.9) == "low"
