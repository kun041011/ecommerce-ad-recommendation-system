import math
from datetime import datetime, timezone
from typing import Dict, List

BEHAVIOR_WEIGHTS = {
    "login": 2,
    "view": 1,
    "search": 1,
    "cart": 3,
    "purchase": 10,
    "review": 5,
    "answer": 5,
    "helpful": 2,
}

DECAY_LAMBDA = 0.1


def time_decay(days_ago: float) -> float:
    return math.exp(-DECAY_LAMBDA * days_ago)


def calculate_activity_score(behaviors: List[Dict]) -> float:
    now = datetime.now(timezone.utc)
    score = 0.0
    for b in behaviors:
        weight = BEHAVIOR_WEIGHTS.get(b["behavior_type"], 0)
        created = b["created_at"]
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        days_ago = (now - created).total_seconds() / 86400
        score += weight * time_decay(max(0, days_ago))
    return min(100.0, round(score, 2))


def classify_activity_level(score: float) -> str:
    if score >= 60:
        return "high"
    elif score >= 20:
        return "normal"
    return "low"
